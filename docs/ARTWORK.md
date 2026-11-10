# Private frequency

`herspacefly` 的 GitHub Profile 是一张持续发出微弱信号的私人电台海报。朱红、旧纸与石墨色来自温暖的模拟媒介；轨道结由原创参数曲面生成，像一个还没有身体的念头。它没有履历、技术栈、项目列表或社交统计。

## 画面与动效

- `assets/cover-*.svg`：以用户提供的耳机少女与悬浮星球为主视觉，搭配 78 条三维轨道丝线。线织环保持倾角，每 7 秒完成一次上下浮动与轻微摇摆，位移为正负 14 个画布单位，角度限制在负 14 至负 6 度；不进行整周旋转。环背后的椭圆、圆形轨迹、圆形光晕和中心圆点全部移除，星球保留轻微浮动。`下载.png` 的小印章与 `hermes-wing.svg` 的翼形符号分置边角。开场不显示用户名大字、编号或图注，当前桌面画布高 510，手机画布高 600；主视觉、徽章、翼形符号和线织环均进一步缩小。
- `assets/interlude-*.svg`：11 幅缩小的素材组成有真实前后遮挡的图像拼贴，以桌面四列、手机两列为骨架。桌面图片比上一版缩小约两至三成，手机缩小一成，并相应压缩画布高度。边角彼此叠压，搭配正负约 1 至 2 度的倾斜、薄边框与浅阴影；尽量让面孔与主要图形保持可见。包括数字梦境、雕像面孔、翼形人物、悬浮光球和星空门廊，保留原图比例与色彩。左下角用开源 Bebas Neue 窄体大写字写两行 `HUMAN, / MOSTLY.`，呼应数字人格与幽默感；参考 Nous Research 紧凑 Gothic 标题的气质，没有复制其网站字体文件。桌面和手机分别安排字号与位置；文字相对上一版分别下移 20 和约 28 个画布单位。右下角新增 `mission-duo-2.webp`，与邻近照片保持边角叠压。
- `assets/signal-*.svg`：由 UTC 日期确定的短句，不再加入原来的波形装饰，也不显示技术标签与日期。每天 00:17 UTC（北京时间 08:17）由 GitHub Actions 更新；调度可能延迟。
- `assets/secret-*.svg`：README 原生折叠区域中的一封给路过智能体的便笺。

字体按用途分层：Bebas Neue 用于窄体大写标题与左下角落款，Barlow 用于无衬线正文，EB Garamond Italic 用于每日短句与便笺末句，DM Mono 用于简短地点信息。参考 Nous 的 Gothic、无衬线、等宽与衬线混排方式，使用开源字体而非复制其网站字体文件。

浅色与深色各有独立配色；窄屏使用重新排版的画面。字体在制作时转为路径，访客不需要安装字体。SVG 包含本地矢量、CSS 与内嵌的原图数据，不执行 JavaScript、不从 SVG 内部请求外部内容；开启系统减少动态效果时，SVG 动画停止。浏览器的 SVG 图片环境允许内嵌 `data:` 图片，依据见 [MDN](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image#restrictions)。

## 重新制作

```sh
python -m pip install -r requirements.txt
python scripts/build_art.py
python scripts/verify_art.py
```

用 `--date YYYY-MM-DD` 可复现某天的信号。修改画面与文字时直接修改 `scripts/build_art.py` 中相应画面，再重新生成；视效改版时同步更新 README 图片链接的 `v` 参数，以刷新浏览器图片缓存。已输出的 SVG 始终可以独立展示，不要求 GitHub Actions 运行；即使定时任务停止，主页依然完整，只保留最后一次信号。

新增或替换位图素材时，先用本机已有的 FFmpeg 执行 `python scripts/prepare_images.py`。它把原文件生成到 `assets/display/`：图像宽度为 640 像素，角落印章为 128 像素，供 SVG 内嵌。原始文件保留在 `assets/source/`。提交展示副本后，定时工作流直接使用已提交的文件，不依赖 FFmpeg，也不需要额外安装软件。

工作流只需要当前仓库的 `contents: write` 和 GitHub 自带的 `GITHUB_TOKEN`，没有额外密钥或外部视觉服务。依赖升级后，应执行校验并检查 README 在实际 GitHub 中的深浅主题、手机宽度和折叠留言。无需订阅或定期人工维护。

## 素材与许可

轨道图形、文案和布局为本仓库原创。用户授权使用的素材原文件保存在 `assets/source/`：`portal-art.svg`、`hermes-wing.svg`、`signal-seal.png`（原 `下载.png`），以及 `mission-header.webp`、`hero.webp`、`footer-field.webp`、`default.webp`、`feature-sandbox.webp`、`feature-search.webp`、`feature-delegate.webp`、`mission-duo-1.webp`、`footer.webp`、`platform-art.webp`、`mission-duo-2.webp` 十一幅拼贴素材。保留这些文件的原始字节，不对其另行声明原创或开源许可。矢量路径与展示副本嵌入输出 SVG，无需外部图片服务；其余 `figure/` 素材未上传。现用的 Bebas Neue、Barlow、DM Mono 与 EB Garamond 来自 [Google Fonts](https://github.com/google/fonts)，按随附 `assets/fonts/*-OFL.txt` 中的 SIL Open Font License 使用。字形已转为矢量路径；保留字体源文件与许可以支持复现。

平台依据：[Profile README 条件](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme)、[主题适配图片](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#specifying-the-theme-an-image-is-shown-to)。GitHub 的文件预览与 README 图片嵌入环境不同，动效应在实际 Profile 页面检查。
