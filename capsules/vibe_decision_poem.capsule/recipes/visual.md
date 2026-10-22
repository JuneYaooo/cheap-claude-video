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

暗酒红与香槟金、宋体、留白。候选序列和曲线承担解释，终章减掉图表，留下短句与缓慢呼吸的轮廓。

当期的主题、数字、图表数据、字幕与来源放在输入 JSON；模板只保留结构与样式。

以全幅留白替代等距卡片：开场用经过画面的候选与一条决定线建立时间感；推演幕用细线、短横轴与局部大数字；终章减去图表。保持下方字幕安全区，金色只标识当前选择或关键量。

## 全画幅参考配置

使用 `assets/reference-style.json` 与 `decision_reference.py` 场景组件，可生成黑金巨型轮廓字、候选序列、概率曲线、结果点阵与留白终章。运行时通过 `--style` 选择；既有默认配色仍可用。全画幅场景隐藏共享页眉与进度线，具体文案和数据由当期输入提供。
