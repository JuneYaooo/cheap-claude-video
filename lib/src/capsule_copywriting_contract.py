from __future__ import annotations

import copy
from typing import Any


NATURAL_COPY_REVIEW_PROMPT = """【自然表达复审：每次写稿和改稿都执行】
先核对主题、观众要解决的问题和证据，再润色措辞。每段应推进问题、做法或结果；删掉没有具体信息的收益口号、功能罗列和强行反转。
对新稿、时长改写、标题及封面逐句复审，去掉套话、夸张宣传、机械排比、助手口吻和段尾升华。技术步骤可以保留清楚的顺序，不机械禁用标点或连接词。
用明确主语、动作和结果写自然口语；长短句随意思变化。不要堆口头禅、故意语病、脏话或编造第一人称体验来制造真人感。事实、限定条件和用户指定原句优先于文风。
独立听稿应能讲清主题、为什么值得看和如何做。工具教程须用真实操作证明收益；无法证明的效果删去或限定。不要把预制素材切换冒充生成过程。
先改掉发现的问题，再按原要求返回终稿；不把本段要求、审稿过程、分数或 AI 痕迹检测结论放进观众文案。任何改字后重新检查，配音与字幕必须使用同一终稿。
"""


COPYWRITING_STRUCTURE_CONTRACT = {
    "topic_to_angle_required": True,
    "natural_language_review_required": True,
    "hook_variants_required": 3,
    "true_first_line_audit_required": True,
    "viewer_pressure_required": True,
    "counterintuitive_thesis_required": True,
    "concrete_scene_required": True,
    "cover_title_alignment_required": True,
    "required_outputs": [
        "raw_topic",
        "audience_pressure",
        "common_misread",
        "counterintuitive_thesis",
        "viral_angle_candidates",
        "recommended_angle",
        "first_3_seconds",
        "first_20_seconds",
        "script_outline",
        "cover_text",
        "title",
        "risk_notes",
    ],
    "opening_gate": {
        "max_seconds": 3,
        "must_contain_one_of": [
            "concrete pain",
            "identity pressure",
            "counterintuitive verdict",
            "status or control stake",
            "completion gap",
        ],
        "reject_if_only": [
            "background setup",
            "abstract concept explanation",
            "generic advice",
            "soft greeting",
            "metadata-only hook",
        ],
    },
}


COPY_RECIPE_DEFAULT_BODY = """# Copy

## copywriting_structure_contract

- 胶囊不能只保存标题、封面和口播风格；它必须能把用户给的原始话题转成可拍的文案结构。
- 正式写稿前先完成 `topic_to_angle_transform`：原始话题 -> 受众压力 -> 常见误解 -> 反常识判断 -> 可观察场景 -> 可传播对象 -> 传播角度候选。
- 每次至少写 3 个角度候选，并给每个候选标注观众为什么会停留、为什么会看完、为什么会收藏或转发。
- 选中的角度必须输出固定字段：原始话题、传播潜力评分、受众压力、常见误解、真正原因、概念命名、可观察场景、可传播对象、前三秒卡片、前 20 秒口播、完整视频结构、封面文案、标题、风险提醒。
- 标题、封面、第一屏和第一句必须来自同一个最高分角度，不能后期各写各的。
- 文案公式只做内部推理；观众可见文案必须像真人说话，不能出现“钩子、爆款结构、传播资产、留存策略、脚本模板”等制作术语。

## natural_language_review

- 每次初稿与改稿都先检查主题、收益和证据，再删去套话、机械排比、强行反转与功能罗列。保留必要步骤和事实边界，不编造经历，不以口头禅代替自然表达。
- 独立听稿能说清主题与做法后再配音；文案改动须重查，审稿说明不进入口播。

## topic_to_angle_transform

- 不要从解释话题开始；先识别该视频类型里的目标受众、现实压力、利益/身份风险、可观察场景和情绪缺口。
- 把普通话题改写成冲突判断时，只使用抽象占位槽位，例如 `表层问题 A -> 深层机制 B`；最终观众文案再改成自然表达。
- 好角度通常同时具备：明确受众、真实压力、反常识判断、可观察场景、身份/利益风险、一个能被命名的机制。
- 如果话题太泛，先收束成五个槽位：`受众`、`压力`、`可观察场景`、`风险`、`转折`；不要在通用胶囊里沉淀某个具体题材或具体桥段。
- 如果话题太正确，先寻找执行阻力、代价、误判和反直觉结果；找不到这些，就把选题标为低传播潜力，而不是硬套爆款话术。

## real_first_line_gate

- 真正 0 秒出现的第一句必须已经制造痛点、身份压力、反常识判断、明确利益或未闭合的问题。
- 标题或内部备注有 hook 不算；第一句、第一屏可见文字和实际时间线必须对齐。
- 弱开头要重写：寒暄、铺背景、定义概念、泛泛建议、慢解释、抽象价值观、只说“今天聊聊”都不能作为第一句。
- 0-3 秒优先使用结论、刺痛问题、可观察冲突或利益损失；3 秒后再补原因。

## output_contract

- `传播角度候选`: 至少 3 个，每个包含角度句、观众压力、完成期待和风险边界。
- `前三秒卡片`: 1-2 行，必须能独立让人停一下。
- `前 20 秒口播`: 先冲突，再解释，最后打开一个必须继续看的问题。
- `完整视频结构`: 按时间段写清每段作用，不能只有大纲词。
- `封面文案` 和 `标题`: 互相呼应，但不要完全重复；一个负责停留，一个负责搜索/推荐语境。
"""


STRUCTURE_RECIPE_DEFAULT_BODY = """# Structure

## script_structure_contract

- 胶囊规划阶段必须先产出文案结构，再进入分镜、视觉和音频；视觉不是拿关键词配图，而是服务脚本的注意力曲线。
- 0-3s: 给判断、痛点、身份压力或具体冲突；不铺背景。
- 3-8s: 用一句简单 thesis 告诉观众这条要推翻什么误解。
- 8-20s: 给证明、场景、例子或对比，让观众理解这个判断为什么和自己有关。
- 20-35s: 给反转、机制命名、行动路径或更深一层原因。
- 35s 以后: 只保留能增加完播、收藏、转发或余味的段落；没有新信息就收。
- 45-90s 视频可以增加一个 proof/action block，但仍然只能讲一个核心判断。

## viral_structure_gate

- 爆款结构不是保证爆款；它只是提高停留、完播、互动概率的骨架。题材强度、账号人设、素材呈现、首帧、声音和平台分发仍会影响结果。
- 任意话题都可以被改写成更有传播力的角度，但不是任意话题都值得做；如果找不到真实压力、利益风险或可观察场景，应降级为低潜力选题或换话题。
- 写结构时先判断内容力，再包装：观众压力、反常识、可观察场景、身份风险、可验证动作、转发理由至少命中 3 项。
"""


def default_copywriting_structure_contract() -> dict[str, Any]:
    return copy.deepcopy(COPYWRITING_STRUCTURE_CONTRACT)
