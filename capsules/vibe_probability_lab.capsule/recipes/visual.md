---
type: Video Recipe
title: Visual Recipe
description: Visual style, references, characters, scenes, composition, and continuity.
stage: planning
domain: visual
profile: video.okf.capsule.v1
tags:
- visual
---

深青实验台、薄荷绿结果、杏色对照。门、骰子、卡片等真实选择对象占画面中心；结论出现前要保留预测时间。

当期的主题、数字、图表数据、字幕与来源放在输入 JSON；模板只保留结构与样式。

V2 使用带透视地面的选择舞台。实体门板绕侧边收窄，内容与空门揭示同步；右侧窄栏只保留当前轮次和两种策略的结果累计。暖色表示坚持，青绿表示换选，结果揭晓前不提前显示奖品。

## 全画幅参考配置

使用 `assets/reference-style.json` 与 `probability_reference.py` 场景组件，可生成蓝金拱门舞台、米黄纸张与信件、绿黑板、模拟收敛与百门排除。运行时通过 `--style` 选择；既有默认配色仍可用。全画幅场景隐藏共享页眉与进度线，具体文案和数据由当期输入提供。
