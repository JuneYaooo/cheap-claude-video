---
type: Video Recipe
title: Motion Recipe
description: Camera motion, action, transitions, dynamic generation, and editing rhythm.
stage: generation
domain: motion
profile: video.okf.capsule.v1
tags:
- motion
---

# 动效服务解释

沿用卡片弹入、关键词强调、全屏与人物小窗切换等已有形式。每次动画必须对应新信息、操作变化或结果比较。

前后对照使用同一动作和相同观察窗口，标示发生改变的参数。保留足够稳定画面，让观众真正看出修改效果。

真实录屏可按语义剪去等待，保留输入、触发和结果关系。字幕与音效跟随新稿语义时间点，不从参考片机械复制绝对时间戳。

## 数字人专门检查

按出镜区间单独检查人脸和口部区域，排除字幕、贴片、背景变化对运动检测的干扰。对可疑停顿，把成片对应帧与源视频的预期帧比对，区分源素材冻结与合成读取错误。源视频正常而成片停住时，修复取帧和时间映射，不用缩放或叠加动画掩盖。

合成中优先顺序解码；随机定位报告的帧号不能证明实际画面正确。源片段超出有效帧范围时明确报错，不默默用旧帧填满。
