# 推广素材（可直接发布）

> 下面每条文案都用本仓脚本测过 AI 味，分数附在末尾。推广一个「去 AI 味」的工具，文案自己先得像人写的。

---

## 一、GitHub 仓库元信息

**Repository name**：`ai-tell`

**About（≤120 字符）**：

```
检测文本的 AI 味：六维度评分 + 逐句证据 + 七个改写动作。零依赖，可进 CI。Agent Skill。
```

**Topics**：

```
agent-skills  claude-skills  ai-detection  writing  chinese-nlp
content-marketing  chinese  python  cli-tool  ai-agents
```

**Social preview（1280×640）**：左边大字 `AI 味 85.1`，中间一个箭头，右边 `0.0`，底部小字 `ai-tell · 逐句告诉你哪几句露馅了`。

---

## 二、Release v1.0.0

```markdown
## 这是什么

把「这段话是不是太像 AI 写的」从一句模糊的感受，变成一个能解释、能复现、能卡住流水线的数字。

## 三个卖点

- **可解释**：六个维度，每个扣分点都指向具体词、具体句
- **可复现**：纯规则，同一输入永远同一分数，不联网、不调模型
- **可落地**：`--fail-over 60` 直接卡 CI；`--mode doc` 让技术文档不被冤枉

## 实测

| 样本 | 分数 |
| --- | --- |
| 典型 AI 稿 | 85.1 |
| 更极端的 AI 稿 | 91.1 |
| 真实公众号风格 | 8.2 |
| 技术文档（doc 模式） | 10.0 |
| 本仓 README（doc 模式） | 2.2 |

同一篇内容改写前后：**85.1 → 0.0**，字数还少了 20 个。

## 安装

    git clone https://github.com/zhbehx/ai-tell.git ~/.claude/skills/ai-tell

## 局限

测语言特征，不测内容价值；词库中文优先，英文只覆盖句长与具体性两个维度。
```

---

## 三、小红书 / 公众号

**标题（8 选 1）**

1. 我写了个脚本，测自己稿子的「AI 味」，85 分
2. 一眼 AI 的稿子，问题都在这 6 个地方
3. 别再问「这段像不像 AI 写的」了，跑一下就有分
4. 同一篇内容，85 分改到 0 分，字数还少了 20
5. 我把自己写的东西测了一遍，48 分，挺丢人的
6. 这个工具不帮你写，只告诉你哪几句在糊弄
7. 「赋能」「闭环」「抓手」——这三个词一出现，读者就走了
8. 开源了个检测器：六个维度，每句都告诉你哪里露馅

**正文**（AI 味 6.6 分）

> 我把自己写的东西丢进脚本里跑了一遍，48 分。
>
> 满分 100，越高越像 AI。48 分的意思是：能读，但读的人会觉得「这人是不是用 AI 写的」。
>
> 我盯着那几行证据看了很久。它挑出来的句子是这些：
>
> `赋能` `闭环` `抓手` `颗粒度` `底层逻辑`
>
> 我确实写过这些词。不是因为我这么说话，是因为我以为这样显得专业。
>
> 后来我把这套判断做成了六个维度：
>
> 1️⃣ **套话黑话**——`赋能`、`闭环`、`抓手`。用 1 个读者觉得你在糊弄，用 3 个读者划走
> 2️⃣ **空转收尾**——「希望对你有所帮助」。删掉之后信息量一个字不少，这就是判断标准
> 3️⃣ **对称句式**——「不是 A，而是 B」。一句话塞两个判断，读者一个都记不住
> 4️⃣ **结构模板**——前言/背景/总结 + 每段一样长。骨架像模板，不像人在想事
> 5️⃣ **句长均匀**——每句都 20 字，像节拍器。人会突然写一句 4 个字的
> 6️⃣ **具体性缺失**——通篇没有一个能核实的数
>
> 跑出来的效果是这样：
>
> ```
> AI 味：85.1 / 100    一眼 AI：结构、用词、节奏三样都在报警
>   套话黑话   100.0  ████████████████████  权重 24%
>   空转收尾   100.0  ████████████████████  权重 22%
> ```
>
> 同一件事，我改成了这样开头：
>
> ❌ 在当今社交媒体快速发展的时代，小红书已经成为品牌营销的重要阵地。
> ✅ 那条笔记爆的时候，我在外面吃饭。点赞从 200 涨到 1.2 万，我盯着手机看了四十分钟，筷子都没动。
>
> 改完再跑：0 分。字数从 284 变成 264——信息量涨了十倍，字数反而少了。
>
> 这就是 AI 味的本质：它不是写得太长，是用同样的字数说了更少的事。
>
> 脚本零依赖，一个 py 文件。能单独跑，也能挂在 CI 上：`--fail-over 60`，超了就报错，不许发。
>
> MIT，随便用。
>
> 你敢把自己的稿子跑一遍吗？评论区报个分数，我猜大部分人会在 40 以上 👇
>
> `#AI写作` `#文案` `#自媒体运营` `#开源` / `#AI味` `#写作技巧` `#提示词` `#公众号运营` / `#我的工作流`

**首评**

> 补一句：引号里的词不算分。你引用「赋能」和真的用「赋能」是两件事，脚本会先把引号、书名号、行内代码里的内容遮掉再统计。我第一次测自己 README 就是 48 分，原因就是正文里列举了这些词。

---

## 四、X / Twitter（英文）

```
Everyone says "this reads like AI" but nobody can point at the sentence.

So I built a linter for it. Six dimensions, each one names the exact words:

→ jargon density (赋能/闭环/抓手)
→ empty openers & closers ("hope this helps")
→ symmetric "not A but B" overuse
→ template skeleton (intro/body/summary, equal-length sections)
→ sentence-length variance (the metronome)
→ specificity deficit (zero verifiable numbers)

Same input → same score. No model, no network, no vibes.

Calibration:
typical AI draft 85.1
real essay voice 8.2
technical doc (doc mode) 10.0

Rewrote one piece: 85.1 → 0.0, and it got 20 characters shorter. That's the whole
point — AI-sounding isn't "too long", it's saying less with the same words.

Fails CI at 60. MIT. Chinese-first.
```

---

## 五、Show HN

```
Show HN: Ai-tell – a deterministic linter for "this reads like AI"

I kept seeing the same complaint about generated text and the same inability to
name what was wrong with it. So I turned the complaint into six measurable
dimensions:

  jargon density, empty framing ("hope this helps"), symmetric-sentence overuse,
  template skeleton, sentence-length variance, and specificity deficit (how many
  verifiable numbers/dates/quotes per 1000 chars).

It's pure rules — no model, no network. Same input, same score, so you can diff
before/after and gate CI on it (--fail-over 60).

Two design decisions worth mentioning:

1. Quoted content is masked before counting. Citing the word "synergy" is not the
   same as using it. My own README scored 48 until I fixed this.
2. There's a --mode doc that drops the "template skeleton" dimension, because
   headings and bullet lists are *correct* in documentation. Scoring a README with
   article weights gives you a false positive.

Calibration on real samples: typical generated draft 85.1, real essay voice 8.2,
technical doc 10.0.

Caveat: the lexicon is Chinese-first (the jargon list is Chinese marketing speak).
English input still gets scored on sentence variance and specificity, but the
jargon dimension is empty. PRs welcome.

github.com/zhbehx/ai-tell
```

---

## 六、首周推广清单

| 渠道 | 素材 | 关键动作 |
| --- | --- | --- |
| GitHub | Release + 3 个 good first issue | issue 要写清验收标准 |
| 小红书 | 第三节正文 + 「85.1 → 0.0」对比图 | 封面主标：`测了一下，我的稿子 85 分` |
| X | 第四节 | 配终端截图，分数可见 |
| Show HN | 第五节 | 周二至周四 UTC 14:00–16:00 |
| 即刻 / V2EX | 只讲一个点：引号遮蔽那个坑 | 不要贴 README |
| 社群 | 一句话 + 链接 | 「做了个测 AI 味的脚本，敢跑一下吗」 |

## 七、让传播自带的三个设计

1. **分数可截图**：终端输出本身就是图，不需要做图。
2. **分数可比较**：朋友之间会互相比「你多少分」——这是天然的社交货币。
3. **结论反直觉**：「字数更少但信息量更大」这句话本身值得转发。
