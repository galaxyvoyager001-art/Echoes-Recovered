# Common App 活动列表填写指南

> **先读这一段。** 这个项目的代码、数字修复、网站和留声机设计，目前主要是在 AI（Claude Code）的协助下完成的。Common App 提交前需要签署声明，确认申请材料是你本人的工作、真实并如实陈述。所以活动描述必须写你**自己真正做了什么**。下面分成两种情况：A 是现在就能如实使用的写法；B 是你完成了第 4 节列出的工作之后才可以使用的写法。

以下数字都可以在仓库中核对：`data/rights_verification_summary.json`、`docs/RESULTS.md`、`data/restored/`。
截至目前：核查 69 首候选，修复 67 首，录制于 1901–1921 年，分布在 24 座城市、19 个国家和地区。

---

## 1. 各字段怎么填

| 字段 | 字数限制 | 建议 |
|---|---|---|
| Activity type | 下拉选择 | **Research**（如果以版权核查和档案研究为主）或 **Computer/Technology**（如果以技术为主）。不确定时选 Research。 |
| Position / Leadership description | 50 字符 | 见第 2 节 |
| Organization name | 100 字符 | 见第 2 节 |
| Activity description | 150 字符 | 见第 2 节 |
| Participation grade levels | 勾选 | 只勾你实际参与的年级 |
| Timing of participation | 勾选 | School year / School break / All year，按实际勾选 |
| Hours per week / Weeks per year | 数字 | **按你本人实际投入的时间填写**，不能把 AI 的运行时间算进去。可以保留日志或 git 提交记录作为依据。 |
| I intend to participate in a similar activity in college | 是/否 | 如果你确实打算继续做数字人文、音频或档案方面的工作，就选是 |

字符数包括空格和标点。下面每一条都已经数过。

---

## 2. 可直接使用的文本

### A. 现在就可以如实使用（写明使用了 AI 工具）

**Position（40 字符）**
```
Founder & Project Lead, Echoes Recovered
```

**Organization（69 字符）**
```
Independent project (Library of Congress National Jukebox recordings)
```

**Description，三选一**

A1（149 字符），强调你作为项目主导者的角色：
```
Directed an AI-assisted project restoring 67 public-domain LoC discs (1901-21) from 24 cities; checked rights for each; launched a map/timeline site.
```

A2（141 字符），强调成果：
```
Restored 67 public-domain 1901-21 discs from 24 cities via AI-assisted DSP; checked rights item by item; mapped them by year and city online.
```

A3（145 字符）：只有在你**确实**逐首听过并调整过参数之后，才能用这一条。
```
Used AI coding tools to restore 67 LoC discs (1901-21, 24 cities); verified rights, tuned and listen-tested each; built an interactive sound map.
```

### B. 完成第 4 节的工作之后可以使用

**Position（42 字符）**
```
Founder; Audio Restoration & Web Developer
```

**Description（146 字符）**：只有在留声机真的做成并能播放、你也亲自调过修复参数之后，才能使用。
```
Built a playable acoustic phonograph; tuned a Python restoration pipeline on 67 LoC discs (1901-21, 24 cities); launched an interactive sound map.
```

---

## 3. 不要写的内容

* "与 Library of Congress 合作""提交给 LoC""被 LoC 收录"：都没有发生。LoC 没有接受公众上传修复版本的渠道。
* 网站访问量、听众人数：目前没有任何数据。
* "first""only" 这类说法：没有核实过。
* "designed my own algorithm""built a phonograph"：在你真正做到之前不要写。
* "AI-free"：修复过程本身确实没有用生成式模型，但代码是在 AI 协助下写的，两件事不要混为一谈。

---

## 4. 在提交之前，把这个项目真正变成你自己的

招生官和面试官可能会追问细节。下面这些事是你本人可以完成的，做完之后用 B 版本就名副其实了：

1. **亲手做出留声机。** 按 `phonograph/README.md` 制作，把实测数据填进第 8 节的记录表；拍照或录视频，记录你遇到的问题和解决办法。
2. **逐首听 A/B 对比。** 打开每首的 `ab_compare.mp3` 和 `removed_component.mp3`，判断有没有处理过度。在 `config/overrides.json` 里为需要的曲目调整参数，重新运行 `scripts/02_restore.py`，并记下你改了什么、为什么改。
3. **读懂并能讲清楚核心方法。** 至少要能用自己的话解释：AR 模型如何检测 click 并插值、Wiener 滤波为什么要设增益下限、为什么不自动修正速度、为什么排除了 2 首 Caruso。
4. **自己动手改一处代码或加一个功能。** 例如逐首判断 wow 并做修正，或者给网站加一个功能。这样你就有一段完全属于自己的工作可以讲。
5. **把成果发布出去。** 用你自己的账户把归档包上传到 Internet Archive（`archive_package/internet_archive_upload.csv`），或者用 GitHub Pages 发布网站。上传之后，"公开发布"才是事实。
6. **记录时间。** 自己的投入时间是 Hours/week 的依据。

---

## 5. 想写得更详细时

150 字符放不下的内容，可以写在 **Additional Information**（最多 650 词）里，但同样要如实说明哪些工作借助了 AI、哪些是你自己完成的。例如：

> I led Echoes Recovered, a project to restore early acoustic recordings from the Library of Congress National Jukebox. I set the goals, and I checked the Rights & Access statement of each of 69 candidate discs; 67 qualified as published before 1923. I used an AI coding assistant to write a Python restoration pipeline (click interpolation, Wiener noise reduction, band-limited filtering) and an interactive map of the recordings by year and city, from Camden to Bogotá, Buenos Aires and Osaka. I then [describe what you personally did: listening tests, parameter changes, building the phonograph, what you learned].

方括号里的内容必须写你本人真正做过的事。

---

## 6. 成果核对数据（来自仓库）

* 候选 69 首；通过版权核查并修复 67 首；排除 2 首（无法证明 1923 年前发行）
* 录制年份 1901–1921；24 座城市；19 个国家和地区
* surface noise 中位数：-36.2 → -45.9 dBFS；脉冲噪声中位数：约 820 → 约 56 次/分钟
* 留声机：目前是设计方案，**尚未制作**
* 正式的人耳听辨测试：**尚未进行**
