#!/usr/bin/env python3
"""ai-tell：检测文本里的「AI 味」，给出可解释的分数与逐句证据。

设计原则：
  1. 每个扣分项都指向一个可指认的句子，不给玄学总分。
  2. 分越高越像 AI。60 分是「一眼 AI」的常见分界线。
  3. 只统计语言特征，不判断内容对错，也不联网。

用法：
    python scripts/ai_tell.py draft.md
    python scripts/ai_tell.py draft.md --explain        # 逐句证据
    python scripts/ai_tell.py draft.md --json
    python scripts/ai_tell.py draft.md --fail-over 60   # 超过阈值退出码 1
    type draft.md | python scripts/ai_tell.py -

退出码：0 正常；--fail-over 触发时 1；文件错误 2。
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# ---------------------------------------------------------------- 模式库

# 一、套话与黑话（出现即扣，权重高）
JARGON = [
    "赋能", "闭环", "抓手", "颗粒度", "底层逻辑", "认知升级", "组合拳", "护城河",
    "顶层设计", "降本增效", "对齐", "拉通", "沉淀", "复用", "打法", "心智",
    "价值锚点", "生态位", "第二曲线", "飞轮", "势能", "破圈", "出圈",
    "方法论", "体系化", "全链路", "端到端", "人货场", "场景化", "结构化思维",
    "深度赋能", "全面赋能", "持续赋能", "长效", "抓手级", "矩阵式",
]

# 二、空转收尾与开场（AI 最爱）
EMPTY_FRAME = [
    "希望对你有所帮助", "希望对你有帮助", "希望对大家有帮助", "希望这些内容",
    "让我们一起", "让我们共同", "总而言之", "综上所述", "总的来说",
    "值得一提的是", "不难发现", "不难看出", "众所周知", "由此可见",
    "在这个快速变化的时代", "在当今", "随着社会的发展", "随着科技的发展",
    "在信息爆炸的时代", "相信大家都", "不知道你有没有发现",
    "以上就是", "感谢阅读", "感谢观看", "欢迎点赞收藏",
]

# 三、对称句式（排比过载）
PARALLEL = [
    r"不是[^。！？\n]{2,20}而是[^。！？\n]{2,20}",
    r"不仅[^。！？\n]{2,20}而且[^。！？\n]{2,20}",
    r"既[^。！？\n]{2,20}又[^。！？\n]{2,20}",
    r"与其[^。！？\n]{2,20}不如[^。！？\n]{2,20}",
    r"一方面[^。！？\n]{2,40}另一方面",
    r"首先[^。！？\n]{0,60}[。；\n][^。]*其次",
]

# 四、结构模板（骨架级 AI 味）
STRUCT_PATTERNS = [
    (r"^\s*#*\s*(前言|引言|背景|概述|简介|结语|总结|写在最后|后记)\s*$", "模板小标题"),
    (r"^\s*(一|二|三|四|五)[、.]\s*\S", "序号小标题"),
    (r"^\s*首先[，,]", "首先/其次式分段"),
    (r"^\s*(最后|最终)[，,]", "最后收尾式分段"),
]

# 五、抽象大词（具体性缺失）
ABSTRACT = [
    "重要性", "必要性", "关键性", "意义重大", "深远影响", "至关重要",
    "核心要素", "关键因素", "多种因素", "各方面", "多维度", "全方位",
    "极大提升", "大幅提高", "显著改善", "有效促进", "充分发挥",
    "不断优化", "持续完善", "深入探索", "积极推动",
]

# 六、可验证的具体性信号（加分，抵抗 AI 味）
SPECIFIC = [
    r"\d+(?:\.\d+)?\s*(?:%|个|人|家|次|天|周|月|年|小时|万|千|元|倍|分|条|版|GB|ms|秒)",
    r"\d{1,2}\s*[/月.-]\s*\d{1,2}",
    r"[A-Z][a-zA-Z]{2,}",
    r"第[一二三四五六七八九十\d]+(?:次|版|轮|步)",
    r"「[^」]{1,20}」",
]

SENT_SPLIT = re.compile(r"[。！？!?\n]")
CJK = re.compile(r"[\u4e00-\u9fff]")

# 被引用的词不算「用了这个词」：引号内、中文书名号内、行内代码内的内容先遮蔽再统计。
QUOTED = re.compile(r"`[^`\n]{1,80}`|「[^」\n]{1,80}」|“[^”\n]{1,80}”|\"[^\"\n]{1,80}\"")


def mask_quotes(text: str) -> str:
    """把引号/代码里的内容替换成等长空白，保留位置与长度，避免误判「引用了这个词」。"""
    return QUOTED.sub(lambda m: " " * len(m.group(0)), text)


def sentences(text: str) -> list[tuple[int, str]]:
    """返回 (行号, 句子)。保留行号便于指认。"""
    out: list[tuple[int, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for s in SENT_SPLIT.split(line):
            s = s.strip().lstrip("#>-*•·| ").strip()
            if len(CJK.findall(s)) >= 6:
                out.append((lineno, s))
    return out


def cjk_len(s: str) -> int:
    return len(CJK.findall(s))


def find_terms(text: str, terms: list[str]) -> list[tuple[str, int]]:
    hits = []
    for t in terms:
        start = text.find(t)
        while start != -1:
            hits.append((t, start))
            start = text.find(t, start + len(t))
    return hits


# ---------------------------------------------------------------- 六维打分

def score_jargon(text: str) -> tuple[float, list[str]]:
    text = mask_quotes(text)
    hits = find_terms(text, JARGON)
    per_100 = len(hits) / max(1, cjk_len(text)) * 1000
    # 每千字 3 个黑话即 100 分
    s = min(100.0, per_100 / 3 * 100)
    detail = sorted({h[0] for h in hits})
    return s, detail


def score_empty_frame(text: str) -> tuple[float, list[str]]:
    text = mask_quotes(text)
    hits = find_terms(text, EMPTY_FRAME)
    s = min(100.0, len(hits) * 34.0)
    return s, sorted({h[0] for h in hits})


def score_parallel(text: str) -> tuple[float, list[str]]:
    text = mask_quotes(text)
    hits = []
    for pat in PARALLEL:
        hits += [m.group(0)[:30] for m in re.finditer(pat, text)]
    sents = max(1, len(sentences(text)))
    density = len(hits) / sents * 100
    s = min(100.0, density / 8 * 100)  # 每 8% 句子带对称句式即满分
    return s, hits[:6]


def score_structure(text: str) -> tuple[float, list[str]]:
    hits = []
    for pat, label in STRUCT_PATTERNS:
        for m in re.finditer(pat, text, re.M):
            hits.append(f"{label}：{m.group(0).strip()[:20]}")
    # 无序列表项占比过高也是骨架味
    lines = [l for l in text.splitlines() if l.strip()]
    bullets = [l for l in lines if re.match(r"^\s*[-*•·]\s", l)]
    if lines and len(bullets) / len(lines) > 0.55 and len(bullets) >= 6:
        hits.append(f"列表占比过高：{len(bullets)}/{len(lines)} 行是列表项")
    s = min(100.0, len(hits) * 25.0)
    return s, hits[:8]


def score_abstract(text: str) -> tuple[float, list[str]]:
    text = mask_quotes(text)
    hits = find_terms(text, ABSTRACT)
    per_1000 = len(hits) / max(1, cjk_len(text)) * 1000
    s = min(100.0, per_1000 / 4 * 100)
    return s, sorted({h[0] for h in hits})


def score_rhythm(text: str) -> tuple[float, list[str]]:
    sents = [cjk_len(s) for _, s in sentences(text)]
    if len(sents) < 5:
        return 0.0, []
    mean = statistics.mean(sents)
    sd = statistics.pstdev(sents)
    cv = sd / mean if mean else 0
    # 人写文本句长变异系数通常在 0.4 以上；AI 常在 0.25–0.40
    s = max(0.0, min(100.0, (0.40 - cv) / 0.15 * 100))
    note = []
    if cv < 0.40:
        note.append(f"句长过于均匀（均值 {mean:.0f} 字，变异系数 {cv:.2f}）")
    return s, note


def score_specificity(text: str) -> tuple[float, list[str]]:
    """具体性越低越像 AI：这一项是反向的，返回「AI 味贡献」。"""
    n = 0
    for pat in SPECIFIC:
        n += len(re.findall(pat, text))
    per_1000 = n / max(1, cjk_len(text)) * 1000
    # 每千字 6 个具体信号算及格线；越少越像 AI
    if per_1000 >= 12:
        return 0.0, []
    s = min(100.0, (12 - per_1000) / 12 * 100)
    return s, [f"具体信号偏少：每千字 {per_1000:.1f} 个（数字/型号/日期/引号原话）"]


# article：公众号/小红书/口播/发言这类「文章」，结构模板也是 AI 味
# doc：技术文档/README/说明书，小标题与列表本来就是必需品，不计入结构模板
WEIGHTS = {
    "article": {
        "套话黑话": 0.24, "空转收尾": 0.22, "对称句式": 0.16, "结构模板": 0.14,
        "抽象大词": 0.14, "句长均匀": 0.10, "具体性缺失": 0.14,
    },
    "doc": {
        "套话黑话": 0.30, "空转收尾": 0.26, "对称句式": 0.14, "结构模板": 0.0,
        "抽象大词": 0.16, "句长均匀": 0.04, "具体性缺失": 0.10,
    },
}


def analyze(text: str, mode: str = "article") -> dict:
    weights = WEIGHTS[mode]
    dims: dict[str, tuple[float, list[str]]] = {
        "套话黑话": score_jargon(text),
        "空转收尾": score_empty_frame(text),
        "对称句式": score_parallel(text),
        "结构模板": score_structure(text),
        "抽象大词": score_abstract(text),
        "句长均匀": score_rhythm(text),
        "具体性缺失": score_specificity(text),
    }
    total_w = sum(weights.values()) or 1.0
    score = sum(dims[k][0] * weights[k] for k in weights) / total_w
    score = round(min(100.0, score), 1)

    if score >= 75:
        verdict = "一眼 AI：结构、用词、节奏三样都在报警"
    elif score >= 60:
        verdict = "很像 AI：读者会觉得「说不清哪里不对，但就是不像人写的」"
    elif score >= 40:
        verdict = "有点 AI 味：能读，但缺少人味的具体细节"
    elif score >= 20:
        verdict = "基本像人：个别句子有模板痕迹"
    else:
        verdict = "很有人味：细节密度和节奏都自然"

    return {
        "score": score,
        "verdict": verdict,
        "mode": mode,
        "cjk_chars": cjk_len(text),
        "dimensions": {k: round(v[0], 1) for k, v in dims.items()},
        "evidence": {k: v[1] for k, v in dims.items() if v[1]},
        "weights": weights,
    }


BAR = "█"


def render(r: dict, explain: bool) -> str:
    lines = []
    lines.append(f"AI 味：{r['score']} / 100    {r['verdict']}")
    lines.append(f"字数：{r['cjk_chars']} 个汉字   模式：{r['mode']}")
    lines.append("")
    for k, w in sorted(r["weights"].items(), key=lambda x: -r["dimensions"][x[0]] * x[1]):
        v = r["dimensions"][k]
        filled = int(round(v / 100 * 20))
        lines.append(f"  {k:<6} {v:5.1f}  {BAR * filled}{'·' * (20 - filled)}  权重 {w:.0%}")
    if explain and r["evidence"]:
        lines.append("")
        lines.append("证据（按维度）：")
        for k, items in r["evidence"].items():
            lines.append(f"  [{k}]")
            for it in items:
                lines.append(f"    - {it}")
    lines.append("")
    if r["score"] >= 60:
        lines.append("结论：先改最上面那一项，它贡献最大。不要整篇重写，先删套话与空转句。")
    else:
        lines.append("结论：可发。若还想更像人，加两个具体数字或一句失败经历。")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="检测文本的 AI 味")
    ap.add_argument("file", nargs="?", default="-", help="文本文件；- 表示标准输入")
    ap.add_argument("--explain", action="store_true", help="输出逐维度证据")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-over", type=float, default=None, help="分数超过该值时退出码 1")
    ap.add_argument("--mode", choices=["article", "doc"], default="article",
                    help="article=文章（默认）；doc=技术文档/README（不计结构模板）")
    args = ap.parse_args(argv)

    if args.file == "-":
        text = sys.stdin.read()
    else:
        p = Path(args.file)
        if not p.is_file():
            print(f"找不到文件：{p}", file=sys.stderr)
            return 2
        text = p.read_text(encoding="utf-8-sig")

    if cjk_len(text) < 30:
        print("文本太短（不足 30 个汉字），检测结果不可靠。", file=sys.stderr)
        return 2

    r = analyze(text, args.mode)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(render(r, args.explain))

    if args.fail_over is not None and r["score"] > args.fail_over:
        return 1
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
