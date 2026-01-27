/// 学习记录模型
class LearningRecord {
  final String id;
  final String title;
  final String description;
  final String type; // question, practice, review
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  LearningRecord({
    required this.id,
    required this.title,
    required this.description,
    required this.type,
    required this.timestamp,
    this.metadata,
  });

  factory LearningRecord.fromJson(Map<String, dynamic> json) {
    return LearningRecord(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      type: json['type'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'type': type,
      'timestamp': timestamp.toIso8601String(),
      'metadata': metadata,
    };
  }
}
