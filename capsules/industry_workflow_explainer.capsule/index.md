---
okf_version: '0.1'
type: Video Capsule Bundle Index
title: 行业岗位 AI 提效讲解
description: 围绕一个岗位的重复任务，从真实材料、整理判断、具体产物到人工修改和下次复用，写出有工作细节的自然口播，并衔接实操演示。
profile: video.okf.capsule.v1
primary_workflow: tool_demo_explainer
tags:
- industry-workflow
- natural-narration
- tool-tutorial
- digital-human
---

# 行业岗位 AI 提效讲解

围绕一个岗位的重复任务，从真实材料、整理判断、具体产物到人工修改和下次复用，写出有工作细节的自然口播，并衔接实操演示。

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
