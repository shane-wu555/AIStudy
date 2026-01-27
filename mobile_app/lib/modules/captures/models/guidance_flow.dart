import 'guidance_step.dart';

/// 导学流程：强调“怎么学”而不是直接给答案
class GuidanceFlow {
  final String sessionId;
  final String? taskId;
  final List<GuidanceStep> steps;

  GuidanceFlow({required this.sessionId, required this.steps, this.taskId});

  factory GuidanceFlow.fromJson(Map<String, dynamic> json) {
    final stepsJson = json['steps'] as List<dynamic>? ?? [];
    final steps = stepsJson
        .map((e) => GuidanceStep.fromJson(e as Map<String, dynamic>))
        .toList();

    return GuidanceFlow(
      sessionId:
          json['session_id']?.toString() ??
          json['task_id']?.toString() ??
          'session_temp',
      taskId: json['task_id']?.toString(),
      steps: steps.isNotEmpty ? steps : _fallbackStepsFromJson(json),
    );
  }

  /// 当后端暂未返回显式 steps 时，用现有字段构造一个基础导学流程
  static List<GuidanceStep> _fallbackStepsFromJson(Map<String, dynamic> json) {
    final List<GuidanceStep> steps = [];

    final analysis = json['analysis'] as Map<String, dynamic>?;
    final message = json['message']?.toString();
    final content = json['content']?.toString();

    if (analysis != null) {
      steps.add(
        GuidanceStep(
          stepId: 'step_read',
          title: '先读懂题目',
          hint: analysis['extracted_text']?.toString() ?? message ?? content,
          type: analysis['type']?.toString(),
          extra: analysis,
        ),
      );
      steps.add(
        GuidanceStep(
          stepId: 'step_plan',
          title: '思考解题思路',
          hint: '根据题干信息，列出已知条件和未知量，尝试画图或列方程。',
          type: 'planning',
        ),
      );
      steps.add(
        GuidanceStep(
          stepId: 'step_try',
          title: '动手尝试第一步',
          hint: '先完成你最有把握的一步，遇到卡顿再点击对应步骤追问。',
          type: 'practice',
        ),
      );
      return steps;
    }

    final baseText = message ?? content;
    if (baseText != null && baseText.isNotEmpty) {
      steps.add(
        GuidanceStep(
          stepId: 'step_focus',
          title: '明确问题',
          hint: baseText,
          type: 'question',
        ),
      );
      steps.add(
        GuidanceStep(
          stepId: 'step_understand',
          title: '理解关键概念',
          hint: '找到题目中的关键概念或公式，先回顾它们的含义和用法。',
          type: 'concept',
        ),
      );
      steps.add(
        GuidanceStep(
          stepId: 'step_solve',
          title: '分步求解',
          hint: '将大题拆成2-3个小目标，逐步推进。',
          type: 'solve',
        ),
      );
    }

    if (steps.isEmpty) {
      steps.addAll([
        GuidanceStep(
          stepId: 'step_1',
          title: '理解题目',
          hint: '先用自己的话复述题目，确认理解无误。',
          type: 'understand',
        ),
        GuidanceStep(
          stepId: 'step_2',
          title: '列出已知和未知',
          hint: '把题目给出的条件和需要求的量写出来。',
          type: 'analysis',
        ),
        GuidanceStep(
          stepId: 'step_3',
          title: '选择方法',
          hint: '想一想可以用哪些方法（例如画图、代数、几何关系等）。',
          type: 'method',
        ),
      ]);
    }

    return steps;
  }
}
