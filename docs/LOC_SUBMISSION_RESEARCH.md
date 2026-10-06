# Library of Congress 是否接受公众提交修复版本？调研结论

调研日期：2026-10-06。所有结论都来自下面列出的 LoC 官方页面，以及本项目对 LoC JSON API 的实际调用。

## 结论（一句话）

**Library of Congress 目前没有面向公众"上传修复版本音频"的正式渠道。** 本项目**没有**向 LoC 提交或上传任何文件，也没有声称已经提交。现有的官方途径只有一个：**向 Recorded Sound Section 发邮件提出"捐赠意向"**。这是由馆员审核的实体或数字馆藏捐赠流程，而不是公众上传系统，并且馆方明确表示要避免重复馆藏。我们的修复版本源自 LoC 自己的馆藏，被接收的可能性很低。因此本项目改为准备一套完整的**公开发布与归档材料**（见 `archive_package/`），并保留全部 LoC attribution。

## 逐项核查

| LoC 渠道 | 用途 | 是否适用于"修复后的数字音频" | 依据 |
|---|---|---|---|
| **Recorded Sound Section 捐赠（sounddonations@loc.gov）** | 公众或机构向录音部门**提出**实体或非商业录音的捐赠意向 | 只能"提出意向"，需要馆员审核和人工审批；馆方要求避免重复，商业录音只有少量会被接收 | [Donations 页面](https://www.loc.gov/programs/national-recording-preservation-board/about-this-program/donations/)：需要在邮件里提供姓名、地址、电话、物品描述（标题、艺人、唱片公司、数量）和物理状况；"unnecessary duplication must be avoided" |
| **Recorded Sound Research Center / Ask a Librarian** | 研究咨询 | 不接收提交；页面没有提到接收数字音频 | [ask.loc.gov/recorded-sound](https://ask.loc.gov/recorded-sound/) |
| **National Jukebox 联系邮箱（Jukebox@loc.gov）** | 关于 Jukebox 内容的问题与反馈 | 是联系渠道，不是投稿渠道 | Jukebox 页面上的联系信息（经搜索引擎核实） |
| **By the People（crowd.loc.gov）** | 志愿者转写、审核、标注**文本**文档 | 不接收音频或修复作品 | [By the People](https://crowd.loc.gov/)（Concordia 平台）；[LoC Labs 说明](https://labs.loc.gov/work/experiments/crowd) |
| **LoC Labs National Jukebox 数据包** | 机器可读的 5,882 条 Jukebox 录音与元数据 | 只供下载，README 里没有任何接收衍生作品的机制 | [data.labs.loc.gov/jukebox](https://data.labs.loc.gov/jukebox/README.html)：数据包说明 "All recordings published before January 1, 1923 entered the public domain on January 1, 2022 under the Music Modernization Act of 2018." |
| **Recorded Sound Division 馆藏政策** | 馆藏范围说明 | 说明收藏范围包括各种格式，历史上主要依靠个人和企业捐赠；没有公众上传流程 | [Collection overview: sound](https://www.loc.gov/acq/devpol/colloverviews/sound.html) |

## 本项目为"官方渠道"实际完成到哪一步

* 已起草一封**捐赠咨询邮件**：`archive_package/LOC_DONATION_INQUIRY_DRAFT.md`。邮件需要你填写本人的姓名、地址和电话，并由你决定是否发送。我**没有**发送它，原因有三：一是需要你的个人信息；二是这是以你的名义对外联系一个机构；三是按馆方的重复馆藏政策，这批衍生文件很可能不会被接收。
* 邮件里说明了：素材来源（逐条 LoC 链接）、版权核查方式、修复方法、文件格式和校验和。如果馆方回复愿意了解，可以直接附上 `archive_package/catalog.csv` 和方法文档。

## 替代的公开发布路径（已准备好材料，未上传）

| 平台 | 已准备的材料 | 发布前需要你完成的人工步骤 |
|---|---|---|
| **Internet Archive**（社区音频合集 `opensource_audio`；其 Great 78 Project 也欢迎 78 转唱片的数字化内容） | `archive_package/internet_archive_upload.csv`：每首一个 identifier，包含修复 FLAC/MP3、A/B 对比、日志、频谱图、LoC 原始 FLAC 和标签图 | 注册 archive.org 账户 → `pip install internetarchive` → `ia configure` → `ia upload --spreadsheet=archive_package/internet_archive_upload.csv` |
| **Wikimedia Commons** | `archive_package/commons/<id>.wikitext` 描述页草稿（`{{Information}}` + `{{PD-US-record-expired}}`） | 用你自己的账户上传；建议上传无损的 restored.flac；上传前逐条确认许可模板 |
| **GitHub 仓库 + Sound Time Map 网站** | 本仓库；`site/` 可以直接用 GitHub Pages 发布 | 在仓库设置中打开 Pages（root 目录），网站地址为 `/site/` |

**Attribution（所有平台都必须保留）：** "Library of Congress, National Jukebox." 外加每条录音的 LoC item URL。本项目是独立项目，与 LoC 没有合作或隶属关系，任何发布文字都不应暗示 LoC 认可。
