# Vibe 知识视频模板

四套本地程序绘图预设，把知识解释转成可参与的图解。第二版加入分风格的场景组件：概率舞台逐轮揭晓、电影式决策轨道、城市路网车辆、暖纸人物学习场景。每套配方保留叙事顺序、视觉和动效规则；当期内容由独立 JSON 提供。

| 预设 | 表达结构 | 随附示例 |
| --- | --- | --- |
| `vibe_probability_lab` 概率实验室 | 选择 → 揭晓 → 比例 / 穷举 → 规则边界 | 三门问题 |
| `vibe_decision_poem` 人生算法诗 | 情境 → 候选序列 → 曲线 → 情绪收束 | 最优停止 |
| `vibe_system_blueprint` 系统蓝图 | 网络 → 单变量改变 → 流量与计算 → 整体结果 | 布雷斯悖论 |
| `vibe_learning_workbench` 学习工作台 | 现场练习 → 遮挡回忆 → 反馈 → 可重复行动 | 主动回忆 |

这些是 `preset`：各已有一个主题的样片验证，尚未完成跨多个主题的稳定性验证。默认输出 1920×1080、30fps、烧录字幕、SRT 和原创程序器乐，无旁白。当前只支持 16:9。

## 安装与运行

需要完整 Capsule Cinema 仓库、Python 3.12、Pillow、numpy、PyYAML、FFmpeg / FFprobe，以及有使用权限且包含所需字符的中文、拉丁字体。渲染器复用仓库内 `dark_gold_knowledge_film` 的基础绘图库；独立胶囊 ZIP 不包含整个运行时。

```bash
python3.12 -m pip install Pillow numpy PyYAML
python3.12 scripts/render_vibe_template.py \
  --capsule vibe_probability_lab \
  --input examples/vibe_knowledge/vibe_probability_lab.json \
  --out output/probability-preview \
  --font /absolute/path/to/chinese-font.ttf \
  --latin-font /absolute/path/to/latin-font.ttf \
  --preview
```

审阅 `qa/review_contact_sheet.jpg` 后，去掉 `--preview`，使用一个新的输出目录渲染成片。可用 `--width 1280 --fps 24` 导出低分辨率版本。已有 `release/final.mp4` 时会拒绝覆盖。

渲染后执行基础验证：

```bash
python3.12 scripts/validate_edit_plan.py --workspace output/probability-film
python3.12 scripts/local_video_qa.py \
  --run-dir output/probability-film \
  --aspect-ratio 16:9 --min-duration 45 --expect-audio \
  --output output/probability-film/qa/local_video_qa.json
```

以上目录应替换为实际成片目录。基础检查覆盖媒体元数据、音轨、时长和时间线；发布前还需检查全部文字、图形含义、动画过程与音频听感。自动技术检查不代表完整内容审片。

## 替换选题

从 `examples/vibe_knowledge/` 复制对应 JSON，修改 `title`、`description`、`sources` 和 `scenes`。每幕包含 `kind`、`heading`、`duration`、`data` 和带起止时间的 `captions`。数据来源需对应当期事实。`reference_analysis` 用来记录参考片及实际改编方式，不复制作者身份或音画素材。

- 每幕 3–30 秒；字幕每段不超过 46 个字符，不可重叠或越出本幕时间。
- `doors`：三门场景，支持指定选中门、开启门、门下说明与切换指示。
- `matrix`：按比例显示点阵；也可用 `cases` 和 `columns` 展示穷举表。理论比例和实际模拟须明确区分。
- `bars`：`values`、`labels`、可选 `display` 和 `highlight`。
- `sequence`：归一化 `values`、观察截止 `cutoff`、比较值 `threshold`；`stop_on_record` 在观察期后第一个超出比较值的候选处停止。
- `curve`：`points` 与 `marker` 使用 `[0,1]` 画布坐标。启用 `percent_axes` 后，纵轴标签按 `y_max` 换算；调用者需把真实值除以纵轴最大值后传入。示例概率曲线用 0.5 为纵轴上限。
- `network`：`nodes` 的 `xy` 使用 1280×720 设计坐标；`edges` 指向节点索引，配置流向、速度、标签和揭晓时间。粒子运动是示意，不是交通仿真。
- `recall`：最多六个 `items`；`hide_at` / `reveal_at` 控制遮挡与恢复。
- `loop`：3–6 个 `items`，按顺序强调当前步骤。
- `statement`：1–3 行结论与一行条件说明。

画面使用 1280×720 逻辑画布，成片按比例放大。标题和图表标签自动缩小到限定宽度；仍应先预览，避免长文造成字体过小。字体文件不随配方分发。

## 风格场景组件

`scripts/vibe_scenes/` 为四套风格分别提供组件模块，每个模块导出 `DRAWERS` 和 `validate_scene(scene)`。共享渲染器只加载固定的本地模块，不接受输入 JSON 指定可执行代码路径。基础组件继续可用，复杂场景可与基础图表组合。

- `probability_*`：舞台选择、主持人规则、逐轮穷举、概率分组、规则边界和收束；计数基于实际枚举结果，必须注明不是随机实测。
- `decision_*`：流动候选、模型条件、停止轨道、函数曲线、概率环和留白结尾；候选轨道在选定项停止，后续候选保持未知。
- `system_city`：四节点路网的前后对照、方向车辆与同步计算。输入总流量、流量除数、固定路段时间与捷径时间；验证器要求参数满足该示例的路线选择前提。
- `learning_*`：人物、书桌、书页、回忆遮挡、核对与日历；用具体动作承载解释。

新组件的字段与默认示例见对应模块和 `examples/vibe_knowledge/`。完整成片之外，可先用不同模型参数、候选序列或练习词组预览，检查模块是否仍符合新内容。

## 全画幅参考风格

`*_reference.py` 组件提供四种更完整的场景语言：蓝金舞台与纸张叙事、黑金数学可视化、夜景城市路网、暗蓝简笔教学。对应 `examples/vibe_knowledge/vibe_*_reference.json` 和 `.style.json` 分别保存内容与配色；原有预设和示例仍可运行。

```bash
python3.12 scripts/render_vibe_template.py \
  --capsule vibe_system_blueprint \
  --input examples/vibe_knowledge/vibe_system_reference.json \
  --style examples/vibe_knowledge/vibe_system_reference.style.json \
  --out output/system-reference-preview \
  --font /absolute/path/to/chinese-font.ttf \
  --latin-font /absolute/path/to/latin-font.ttf \
  --preview
```

每幕的 `full_bleed: true` 隐藏共享页眉、页码及进度线，让场景自行构图；`show_captions: false` 允许文字直接排入画面，同时保留 SRT 导出；`caption_color` 可调整烧录字幕颜色。`--style` 仅覆盖当前运行的配色，不修改胶囊默认值。

参考风格示例使用重新编写的文案、程序绘制的几何与原创程序配乐，不包含参考作者的原始音画。参考镜头顺序、素材、字体、镜头运动和声音仍有差异；输入中的 `reference_analysis` 记录已实现元素与差异，技术检查分数不表示视频相似度。

## 输出与打包

`release/` 包含 MP4、封面、SRT 和发布文案；`work/` 保留当期输入、样式、原创配乐、连续画面母版、编辑计划和时间线；`qa/` 包含代表帧。编辑计划引用真实连续画面母版，并以 `scene_map` 标注每幕，不伪造独立镜头文件。

```bash
python3.12 scripts/capsule_package_validate.py capsules/vibe_probability_lab.capsule
python3.12 scripts/capsule_package_pack.py capsules/vibe_probability_lab.capsule \
  --out output/vibe_probability_lab.capsule.zip
```

新主题的脚本和数据留在独立输入中；只有通用方法才回写配方。示例中的知识来源随 JSON 提供，扩写时应重新核验适用条件。
