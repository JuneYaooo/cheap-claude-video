---
type: Video Capsule Card
title: 行业岗位 AI 提效讲解
description: 围绕一个岗位的重复任务，从真实材料、整理判断、具体产物到人工修改和下次复用，写出有工作细节的自然口播，并衔接实操演示。
stage: routing
profile: video.okf.capsule.v1
primary_workflow: tool_demo_explainer
tags:
- industry-workflow
- natural-narration
- tool-tutorial
- digital-human
---

# 行业岗位 AI 提效讲解

## Purpose

围绕一个岗位的重复任务，从真实材料、整理判断、具体产物到人工修改和下次复用，写出有工作细节的自然口播，并衔接实操演示。

## 适用场景

行业岗位的 AI 应用讲解：用一个重复任务讲清材料、操作、成果、人工判断和复用。可先只交付口播，再按确认结果制作视频。

## 使用方式

提供岗位、任务、原来怎么做、可用材料、实际工具和期望产物。先读 [口播配方](recipes/copy.md) 与 [行文结构](recipes/structure.md)，完成写稿和作者自改，再进入分镜。

调用示例：用 `industry_workflow_explainer` 配方，为 {岗位} 写一期 {重复任务} 的 AI 提效口播，工具是 {工具}，先确认文案。

## 不适用

泛趋势评论、工具排行榜、缺少依据的效率宣传，以及代替专业人员作最终决策的内容。

## Stage Reading

- Routing: read `capsule.yaml`, `index.md`, this card, `contracts/input_schema.yaml`, and `contracts/content_scope.yaml`.
- Planning: read the input/content-scope contracts and the recipe files named under `read_order.planning`.
- Generation: read the runtime contract, motion recipe, and asset index.
- QA: read the quality rules and release gates.
- Learning: read promoted lessons only; raw evidence is local-only.
