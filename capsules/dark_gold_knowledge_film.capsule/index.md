---
okf_version: '0.1'
type: Video Capsule Bundle Index
title: 黑金知识动画
description: 用宋体、黑金细线图解和原创器乐解释抽象知识；代码驱动画面，按信息密度分配镜头时长，字幕与配乐随时间线同步。
profile: video.okf.capsule.v1
primary_workflow: procedural_knowledge_film
tags:
- knowledge-explainer
- dark-gold
- mathematical-animation
- code-rendered
- variable-pacing
- landscape
---

# 黑金知识动画

用宋体、黑金细线图解和原创器乐解释抽象知识；代码驱动画面，按信息密度分配镜头时长，字幕与配乐随时间线同步。

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
