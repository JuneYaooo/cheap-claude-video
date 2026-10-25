---
type: Video Capsule Card
title: 行业岗位 AI 提效讲解
description: 有直观成果时先展示效果，再讲任务、制作方法、人工修改与复用；没有合适成果时从具体工作切入，人物按解释需要穿插。
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

有直观成果时先展示效果，再讲任务、制作方法、人工修改与复用；没有合适成果时从具体工作切入，人物按解释需要穿插。

## 适用场景

行业岗位的 AI 应用讲解：用一个重复任务讲清材料、操作、成果、人工判断和复用。可先只交付口播，再按确认结果制作视频。

## 使用方式

提供岗位、任务、原来怎么做、可用材料、实际工具和期望产物。先读 [完整参考口播](assets/writing-reference.txt)、[口播配方](recipes/copy.md) 与 [行文结构](recipes/structure.md)，默认由 Kimi 写初稿，再由 Kimi 自行去 AI 味；先检查已有成果并决定开头模式，确认口播后进入分镜；数字人按解释需要安排，不固定开场。

调用示例：用 `industry_workflow_explainer` 配方，为 {岗位} 写一期 {重复任务} 的 AI 提效口播，工具是 {工具}，先确认文案。

## 不适用

泛趋势评论、工具排行榜、缺少依据的效率宣传，以及代替专业人员作最终决策的内容。

## Stage Reading

- Routing: read `capsule.yaml`, `index.md`, this card, `contracts/input_schema.yaml`, and `contracts/content_scope.yaml`.
- Planning: read the input/content-scope contracts and the recipe files named under `read_order.planning`.
- Generation: read the runtime contract, motion recipe, and asset index.
- QA: read the quality rules and release gates.
- Learning: read promoted lessons only; raw evidence is local-only.
