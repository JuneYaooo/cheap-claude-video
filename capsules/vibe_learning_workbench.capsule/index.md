---
okf_version: '0.1'
type: Video Capsule Bundle Index
title: 学习工作台
description: 用实际练习、信息遮挡和反馈循环，把学习方法变成可执行动作。
profile: video.okf.capsule.v1
primary_workflow: procedural_knowledge_film
tags:
- vibe-knowledge
---

# 学习工作台

用实际练习、信息遮挡和反馈循环，把学习方法变成可执行动作。

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
