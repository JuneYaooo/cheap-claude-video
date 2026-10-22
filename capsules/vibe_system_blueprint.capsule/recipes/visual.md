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

深蓝工程图、青色路径、珊瑚红干预。节点位置跨镜头固定，流量与时间一起显示，前后图使用同一比例。

当期的主题、数字、图表数据、字幕与来源放在输入 JSON；模板只保留结构与样式。

城市地图组件保持节点位置、路线和总流量一致，前后对照只改变需要解释的连接。车辆用有方向的图形，淡色城市块只作空间背景；右侧保留计算区。

## 全画幅参考配置

使用 `assets/reference-style.json` 与 `system_reference.py` 场景组件，可生成夜景城市、弯曲发光路网、耗时数字、纸张与手机插入镜头。运行时通过 `--style` 选择；既有默认配色仍可用。全画幅场景隐藏共享页眉与进度线，具体文案和数据由当期输入提供。
