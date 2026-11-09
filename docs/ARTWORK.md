# Private frequency

`herspacefly` 的 GitHub Profile 是一张持续发出微弱信号的私人电台海报。朱红、旧纸与石墨色来自温暖的模拟媒介；轨道结由原创参数曲面生成，像一个还没有身体的念头。它没有履历、技术栈、项目列表或社交统计。

## 画面与动效

- `assets/cover-*.svg`：以用户提供的耳机少女与悬浮星球为主视觉，搭配 78 条三维轨道丝线。保留附件的蓝白配色与完整矢量路径；轨道缓慢摆动、中心光晕呼吸、星球轻微浮动。开场不再显示用户名大字、编号或图注。
- `assets/interlude-*.svg`：电影散场、数字生命、漫游三个短片段。
- `assets/signal-*.svg`：由 UTC 日期确定的短句与原创波形，画面不显示技术标签与日期。每天 00:17 UTC（北京时间 08:17）由 GitHub Actions 更新；调度可能延迟。
- `assets/secret-*.svg`：README 原生折叠区域中的一封给路过智能体的便笺。

浅色与深色各有独立配色；窄屏使用重新排版的画面。字体在制作时转为路径，访客不需要安装字体。SVG 仅包含本地矢量与 CSS，不执行 JavaScript、不加载外部内容；开启系统减少动态效果时，SVG 动画停止。

## 重新制作

```sh
python -m pip install -r requirements.txt
python scripts/build_art.py
python scripts/verify_art.py
```

用 `--date YYYY-MM-DD` 可复现某天的信号。修改画面与文字时直接修改 `scripts/build_art.py` 中相应画面，再重新生成。已输出的 SVG 始终可以独立展示，不要求 GitHub Actions 运行；即使定时任务停止，主页依然完整，只保留最后一次信号。

工作流只需要当前仓库的 `contents: write` 和 GitHub 自带的 `GITHUB_TOKEN`，没有额外密钥或外部视觉服务。依赖升级后，应执行校验并检查 README 在实际 GitHub 中的深浅主题、手机宽度和折叠留言。无需订阅或定期人工维护。

## 素材与许可

轨道图形、文案和布局为本仓库原创。`assets/source/portal-art.svg` 是用户明确要求加入主页的附件原文件，保留其原始路径与配色，未对其另行声明原创或开源许可；生成器将矢量路径嵌入开场画面，无需外部图片服务。其他 `figure/` 素材未上传。Instrument Serif 与 DM Mono 来自 [Google Fonts](https://github.com/google/fonts)，按随附 `assets/fonts/*-OFL.txt` 中的 SIL Open Font License 使用。字形已转为矢量路径；保留字体源文件与许可以支持复现。

平台依据：[Profile README 条件](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme)、[主题适配图片](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#specifying-the-theme-an-image-is-shown-to)。GitHub 的文件预览与 README 图片嵌入环境不同，动效应在实际 Profile 页面检查。
