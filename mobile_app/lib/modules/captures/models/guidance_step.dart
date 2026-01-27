class GuidanceStep {
  final String stepId;
  final String title;
  final String? hint;
  final String? type;
  final Map<String, dynamic>? geometry; // 用于3D几何演示的数据
  final Map<String, dynamic>? extra;

  GuidanceStep({
    required this.stepId,
    required this.title,
    this.hint,
    this.type,
    this.geometry,
    this.extra,
  });

  factory GuidanceStep.fromJson(Map<String, dynamic> json) {
    return GuidanceStep(
      stepId: json['step_id']?.toString() ?? json['id']?.toString() ?? '',
      title: json['title']?.toString() ?? '学习步骤',
      hint: json['hint']?.toString() ?? json['description']?.toString(),
      type: json['type']?.toString(),
      geometry: json['geometry'] is Map<String, dynamic>
          ? json['geometry'] as Map<String, dynamic>
          : null,
      extra: json,
    );
  }
}
