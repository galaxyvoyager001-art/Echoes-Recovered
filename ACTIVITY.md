# 活动描述（基于实际完成的成果）

以下数字全部可以在仓库中核对：`data/rights_verification_summary.json`、`docs/RESULTS.md`、`data/restored/`。

## 现在就可以如实使用的版本

**中文（约 150 字）**
设计了一台可以亲手制作的机械留声机（指数号角、唱头、唱臂几何均经计算），自己编写历史录音修复算法（AR 模型去 click、Wiener 降噪、有界自适应 EQ，不使用生成式 AI）。从 Library of Congress National Jukebox 逐条核查 54 首候选录音的版权，修复其中 52 首 1901–1921 年的早期留声机唱片（录制于美国、拉丁美洲和欧洲共 16 座城市），并建立交互式 Sound Time Map，按年代和录制城市重新组织和传播这些历史声音。

**English (~50 words)**
Designed a buildable acoustic phonograph and wrote a non-generative restoration pipeline in Python (AR click interpolation, Wiener denoising, bounded EQ). Rights-checked 54 Library of Congress National Jukebox recordings, restored 52 acoustic-era discs (1901–1921) recorded in 16 cities across the US, Latin America and Europe, and built an interactive Sound Time Map organizing them by year and recording city.

**Common App 风格（150 字符以内）**
Rights-checked & restored 52 LoC acoustic-era discs from 16 cities (1901–21) with my own DSP pipeline; built Sound Time Map; designed a phonograph.

## 留声机实物做好并能播放之后，可以改用的版本
> 只有在你真正完成实物、能够播放唱片之后，才使用下面这句。

自己搭建机械留声机，设计历史录音修复算法，从 Library of Congress 修复 52 首早期留声机歌曲，并建立 Sound Time Map，按照年代和录制地点重新组织和传播这些历史声音。

## 不要写进描述里的内容（因为没有发生）
* 没有向 Library of Congress 上传或提交任何文件，也没有与 LoC 合作。LoC 没有接受公众上传修复版本的渠道。
* 网站没有任何访问量数据。
* 修复效果没有经过正式的人耳听辨测试；目前只有客观测量数据（例如 surface noise 中位数从 -34.6 降到 -45.1 dBFS，脉冲噪声中位数从约 817 次/分钟降到约 69 次/分钟）。
* 留声机目前是设计方案，尚未制作。
