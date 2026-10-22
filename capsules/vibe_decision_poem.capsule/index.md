---
okf_version: '0.1'
type: Video Capsule Bundle Index
title: 人生算法诗
description: 用连续几何动画和克制的情绪收束，解释选择模型及其现实边界。
profile: video.okf.capsule.v1
primary_workflow: procedural_knowledge_film
tags:
- vibe-knowledge
---

# 人生算法诗

用连续几何动画和克制的情绪收束，解释选择模型及其现实边界。

# Entry

* [Capsule Card](CARD.md) - Routing summary, purpose, and usage boundary.

# Contracts

* [Input Schema](contracts/input_schema.yaml) - User input requirements and intake fields.
* [Content Scope](contracts/content_scope.yaml) - Series-fixed elements, per-episode content, and forbidden reusable literals.
* [Runtime Contract](contracts/runtime.yaml) - Tool roles, execution constraints, and output contract.
* [Production Contract](contracts/production_contract.yaml) - Required outputs, evidence floor, and modality gates.

# Recipes

* [Structure](recipes/structure.md) - Story beats, pacing, and scene architecture.
* [Copy](recipes/copy.md) - Voiceover, subtitles, titles, cover copy, lyrics, and CTA rules.
* [Visual](recipes/visual.md) - Visual style, references, characters, scenes, and continuity.
* [Audio](recipes/audio.md) - TTS, original audio, BGM, SFX, mix, and sync rules.
* [Motion](recipes/motion.md) - Camera motion, action, transitions, dynamic generation, and editing rhythm.

# Assets

* [Asset Index](assets/index.yaml) - Reusable packaged assets and references. Asset files are not loaded unless needed.

# Quality

* [Rules](quality/rules.yaml) - Machine-readable QA rules.
* [Release Gates](quality/release_gates.yaml) - Required checks before release.

# Learning

* [Promoted Lessons](learning/promoted_lessons.yaml) - Generalized lessons only; raw evidence remains local or archived.

# Examples

* [Illustrative Examples](examples/illustrative.yaml) - Examples for orientation only, not default final content.

## 本地制作

由 Agent 按配方编写当期场景 JSON，再调用项目的 `scripts/render_vibe_template.py`。渲染器与基础绘图库随 Capsule Cinema 运行时安装，独立配方包需要该运行时。先使用 `--preview` 审阅图解，再导出 MP4、字幕、封面与时间线。

## 全幅决策舞台

共享渲染器从 `scripts/vibe_scenes/decision.py` 加载专用镜头；旧版通用组件仍可用于其他排版。专用组件使用同一输入协议（`kind`、`heading`、`duration`、`captions`、`data`）：

- `decision_opening`：`values` 归一化序列、`lines` 两句短文、`kicker` 和 `present_label`。候选经过决定线。
- `decision_conditions`：四条 `items` 与 `note`，按次序显现约束。
- `decision_track`：归一化 `values`、观察数量 `cutoff`、每次出现间隔 `step_seconds`、阈值与区域标签。观察后在首次超出既有最高值时停止；后续候选不提前泄露。
- `decision_curve`：归一化二维 `points`、二维 `marker`、实际纵轴上限 `y_max`、坐标/公式/注释文本。输入负责公式与数据一致性。
- `decision_odds`：两项非负 `values`、匹配的 `labels` 和 `display`。圆环为近似视觉刻度，文字提供准确口径。
- `decision_epilogue`：一至两行 `lines` 与 `note`，只保留一句情绪落点和必要边界。

这些组件保留底部字幕区。首幕、推演与终章采用不同构图密度，避免每幕都重复相同的信息卡片。跨主题复用仍需核对策略是否适用，不自动把任意决策题解释为最优停止问题。
