# Echoes Recovered：早期留声机录音修复与 Sound Time Map

本项目从 **Library of Congress National Jukebox** 筛选 1901–1921 年间以 acoustic recording 技术录制的商业唱片，逐条核实 Rights & Access，下载原始文件，用一套可重复运行的 Python 数字修复流程修复，并把结果组织成按年代和录制城市浏览的交互式网站 **Sound Time Map**。项目还附有一台可以亲手制作的纯机械留声机的设计方案。

> 本项目是独立项目，与 Library of Congress 没有合作或隶属关系。所有录音的出处都是：**Library of Congress, National Jukebox.**

## 实际完成情况（数字均来自仓库内的真实输出）

<!-- RESULTS:START -->
* 共核查 **26** 个 LoC 候选，**24** 首通过版权核查并完成修复，**2** 首被排除（理由见 [docs/RESULTS.md](docs/RESULTS.md)）。
* 录制年份 1901–1921；录制城市（按 LoC 记录）：Camden, New York, Philadelphia。
* Median surface-noise level: **-32.5 dBFS -> -45.1 dBFS** (median change -9.8 dB).
* Median impulses/min (AR detector, k=8): **1485 -> 80**.
* Samples interpolated across clicks: median **2.14%**, max 3.35% per track.
* Energy removed in 300-3000 Hz relative to the original: median **-21.7 dB** (range -33.8 to -10.9 dB).
* Tracks with a 50/60 Hz peak flagged and notched: 1. Speed/pitch corrections applied: 0. Generative/AI processing: none.


逐首数据见 [docs/RESULTS.md](docs/RESULTS.md)。
<!-- RESULTS:END -->

## 文件夹结构

```
Echoes-Recovered/
├── README.md                     本文件
├── ACTIVITY.md                   基于实际成果的活动描述
├── run_all.sh                    一键从头复现全部步骤
├── requirements.txt              Python 依赖（另需 ffmpeg）
├── config/
│   ├── selection.json            候选曲目（LoC item id）+ 项目自写的背景注释
│   └── overrides.json            （可选）逐首手动参数覆盖；本次未使用
├── scripts/
│   ├── 01_fetch_loc.py           LoC JSON API → 版权核查 → 下载 WAV/MP3/唱片标签，记录 SHA-256
│   ├── 02_restore.py             损伤分析 → 逐首参数 → 修复 → 图表、日志、A/B 对比
│   ├── 03_preserve_originals.py  LoC WAV → FLAC，并用 PCM MD5 证明逐位一致
│   ├── 04_build_site.py          生成 Sound Time Map 的数据与地图底图
│   ├── 05_build_archive_package.py  公开发布与归档材料（不上传）
│   ├── 06_bundle_site.py         把网站打包成自包含目录（用于其他托管方式）
│   └── 07_results_table.py       汇总真实结果 → docs/RESULTS.md
├── restoration/                  修复算法（Python 包）
│   ├── analysis.py               surface noise / click / 频带 / hum / 削波 / 音高与 wow 分析
│   ├── dsp.py                    AR 模型、LSAR 插值、Wiener 降噪、滤波、自适应 EQ、变速
│   ├── pipeline.py               由分析结果推导参数并执行整条修复链
│   └── plots.py                  waveform / spectrogram / spectrum 对比图
├── data/
│   ├── rights_verification_summary.json  每个候选的版权核查结论
│   ├── metadata/<id>.json        每首歌的元数据 + 版权记录（含 LoC Rights & Access 原文）
│   ├── originals/<id>/           LoC 原始文件：loc_original.flac（与 LoC WAV 逐位一致）、
│   │                             loc_original.mp3（LoC 原文件）、loc_label.jpg、loc_item.json
│   └── restored/<id>/            restored.flac / .mp3、ab_compare.mp3、removed_component.mp3、
│                                 analysis.json、params.json、restoration_log.md、3 张对比图
├── site/                         Sound Time Map（静态网站）
├── phonograph/                   机械留声机设计：README、design.py、1:1 模板与总图
├── archive_package/              Internet Archive / Wikimedia Commons / LoC 咨询材料
└── docs/
    ├── METHODOLOGY.md            修复方法详述（英文）
    ├── RESULTS.md                逐首修复前后数据（自动生成）
    └── LOC_SUBMISSION_RESEARCH.md  LoC 提交渠道调研结论
```

> **关于原始 WAV：** LoC 的 WAV 母带每个 20–26 MB，仓库里不直接收录（见 `.gitignore`）。仓库保存的是 FLAC 无损副本：解码后的 PCM MD5 与 WAV 完全一致，结果记录在每首的 `metadata/<id>.json → lossless_copy`。`scripts/01_fetch_loc.py` 可以重新下载原始 WAV，并用记录的 SHA-256 校验。LoC 的 MP3 原文件则原样保存在仓库中。

## 1. 歌曲收集与版权核查
* **来源：** 只使用 LoC National Jukebox，通过官方 JSON API（`https://www.loc.gov/item/<id>/?fo=json`）读取。LoC 网页前端有 Cloudflare 人机验证，所以没有用浏览器抓取 HTML；JSON 里的 `rights` 字段就是网页上 "Rights & Access" 栏的原文，脚本把它逐条保存在元数据里。
* **核查规则**（`scripts/01_fetch_loc.py: assess_rights`），四条必须同时满足：
  1. 该条目的 Rights & Access 原文包含 "all recordings published prior to 1923 will enter the public domain"（Music Modernization Act）；
  2. 录制日期早于 1922-01-01。这是额外留出的安全余量，确保发行日期也早于 1923 年；
  3. 有**已发行**的证据：LoC 文件 ID 中带有 Victor/Columbia 唱片编号，并且 LoC 提供了唱片标签图像。按 MMA，**未发行**的 1923 年前录音要到 2067 年才进入公有领域，所以这一条必须满足；
  4. `access_restricted = false`，并且 LoC 提供 WAV 下载。
* **没有因为录音很老就默认可以使用。** 有 2 个候选因为第 3 条被排除：Caruso 的《Over There》（1918）和 Caruso 等人的 Lucia 六重唱（1908）。LoC 没有给出这两条的唱片标签，无法证明它们在 1923 年前发行。
* 1922–1925 年的录音没有收录。按 MMA，1923–1925 年发行的录音现在其实也已进入美国公有领域，但 LoC 的 Rights & Access 原文只明确写了"1923 年以前发行"，项目选择以 LoC 原文为准。
* 每首记录的字段：标题、其他标题、表演者（含 LoC 列出的角色）、录制日期、录制地点（LoC `location` 原样保存）、LoC 音乐类型、项目分类、唱片公司与编号、matrix/take、语言、原始档案页面、原始 WAV/MP3 地址、来源实体唱片的收藏机构、Rights & Access 原文、rights advisory、核查时间与理由。

## 2. 数字修复方法
详见 [docs/METHODOLOGY.md](docs/METHODOLOGY.md)。简要流程：

```
LoC WAV ─► 损伤分析 ─► 逐首参数 ─► 50 Hz 高通 ─► AR 检测 + LSAR 插值去 click（≤4 ms）
        ─► 二次去 crackle（≤1 ms，自动回退）─► 决策导向 Wiener 降噪（导入槽 / 最小统计噪声模板）
        ─► 有效频带之上的 hiss 低通 ─► 有界自适应 EQ（削减号角共振峰）─► 响度匹配 ─► FLAC / MP3
```

* 每首都按自己的分析结果设置参数：click 阈值看脉冲密度，降噪强度和增益下限看信噪比，低通截止频率看实测的有效频带，EQ 范围也看频带。参数和理由都写在 `params.json` 与 `restoration_log.md` 里。
* **不使用生成式 AI**，不做带宽扩展、混响、立体声化或限幅。唯一写入新样本值的环节是 click 插值，它只用相邻的真实样本计算。每首被插值的样本比例都记录在日志中。
* **速度与 wow：** 代码支持常速和变速校正，并会测量音高偏移和 1.0–1.6 Hz 的 wow 峰值。但历史定音标准不统一，旋律和颤音也会干扰测量，所以**本次没有自动修改任何曲目的速度**，测量结果写在日志里，留待人工听辨后再决定。
* **透明度：** 每首都有 `removed_component.mp3`，即"原始减去修复（EQ 之前）"的差值信号，可以直接听修复到底去掉了什么。
* **尚未完成的事：** 没有做正式的人耳听辨测试。参数依据客观测量和图表检查确定。建议先听 A/B 和"被去除的部分"，如有需要，在 `config/overrides.json` 中逐首调整后重新运行。

## 3. Sound Time Map
本地运行：

```bash
python3 -m http.server 8000      # 在仓库根目录运行
# 打开 http://localhost:8000/site/
```

* **时间轴：** 1900–1925，每个点对应一次录音；可以点年份筛选，也可以点单个录音。1922–1925 年以灰色标出"未收录（版权余量）"。
* **地图：** 使用 US Census 州界（us-atlas 3.0.1），在本地投影，不依赖地图瓦片服务。点位只标在 LoC 记录中写明的**城市**（New York、Camden、Philadelphia），不标任何具体地址。
* **详情面板：** 标题、表演者、日期、地点（LoC 原文）、LoC 类型、唱片编号与 matrix/take、演职人员、LoC 原始页面链接、项目背景注释（已标明是项目撰写）、**Original 与 Restored 两个播放器**、"在同一时刻切换"按钮、A/B 文件、被去除部分、修复日志和频谱图。
* 网站直接引用 `data/` 里的文件，不重复存储音频。部署到 GitHub Pages 时选择从仓库根目录发布即可。

## 4. 机械留声机
见 [phonograph/README.md](phonograph/README.md)：原理（唱针 → 针杆 → 振膜 → 唱臂 → 指数号角）、零件清单、尺寸、材料、装配步骤、安全提示和实测记录表。`phonograph/design.py` 生成全部尺寸、1:1 号角纸样、频闪盘和总图。**这是一份设计方案，实物尚未制作。**

## 5. LoC 提交 / 归档
见 [docs/LOC_SUBMISSION_RESEARCH.md](docs/LOC_SUBMISSION_RESEARCH.md)。结论是：**LoC 没有接受公众直接上传修复版本的正式渠道，本项目没有向 LoC 上传或提交任何内容。** 唯一相关的官方途径是向 Recorded Sound Section 发邮件提出捐赠意向（sounddonations@loc.gov），需要馆员人工审核。项目已起草咨询邮件，但没有发送。`archive_package/` 里准备了 Internet Archive 批量上传表、Wikimedia Commons 描述页、目录 CSV、SHA-256 清单和 bag-info，全部保留 LoC attribution。上传需要你本人的账户。

## 复现
```bash
pip install -r requirements.txt     # 另需 ffmpeg
./run_all.sh                        # 下载约 0.6 GB；修复在 4 核机器上约需 15–25 分钟
```

## 许可
见 [LICENSE](LICENSE)：录音在美国属于公有领域（LoC 来源）；项目产出的修复音频、文档和数据以 CC0 发布；代码采用 MIT 许可。
