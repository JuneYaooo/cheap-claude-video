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

暖纸底色、墨绿衣着与书封、陶土铅笔和重点标记。粗细有别的墨线、少量纸张投影；平面简笔人物保留一致的头身比例、短发轮廓和坐姿。

人物必须处在可读的空间关系中：桌面承托书，手臂伸向书或笔，纸张承载回答。避免把每幕退化成圆角卡片。笔记本可作为文字容器，日历仅在时间条件有意义时出现。

暖色场景与深色概率、算法图表形成明显区分。禁止泛化的大脑发光、无来源的神经动画和装饰性百分比。逻辑画布 1280×720；主图范围 y=235–610，字幕约 y=646，重要文字远离底部进度线。

## 全画幅参考配置

使用 `assets/reference-style.json` 与 `learning_reference.py` 场景组件，可生成暗蓝渐晕、黑体黄重点、白色简笔图解与章节行动卡。运行时通过 `--style` 选择；既有默认配色仍可用。全画幅场景隐藏共享页眉与进度线，具体文案和数据由当期输入提供。
