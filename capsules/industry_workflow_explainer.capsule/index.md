---
okf_version: '0.1'
type: Video Capsule Bundle Index
title: 行业岗位 AI 提效讲解
description: 有直观成果时先展示效果，再讲任务、制作方法、人工修改与复用；没有合适成果时从具体工作切入，人物按解释需要穿插。
profile: video.okf.capsule.v1
primary_workflow: tool_demo_explainer
tags:
- industry-workflow
- natural-narration
- tool-tutorial
- digital-human
---

# 行业岗位 AI 提效讲解

有直观成果时先展示效果，再讲任务、制作方法、人工修改与复用；没有合适成果时从具体工作切入，人物按解释需要穿插。

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

* [Asset Index](assets/index.yaml) - Reusable packaged assets and references.
* [完整参考口播](assets/writing-reference.txt) - 初稿与作者自改时读取的完整写作参考。

# Quality

* [Rules](quality/rules.yaml) - Machine-readable QA rules.
* [Release Gates](quality/release_gates.yaml) - Required checks before release.

# Learning

* [Promoted Lessons](learning/promoted_lessons.yaml) - Generalized lessons only; raw evidence remains local or archived.

# Examples

* [Illustrative Examples](examples/illustrative.yaml) - Examples for orientation only, not default final content.
