/// 消息模型
class MessageModel {
  final String id;
  final String content;
  final bool isUser;
  final DateTime timestamp;
  final String? reasoning; // AI推理链路
  final Map<String, dynamic>? metadata; // 附加元数据

  MessageModel({
    required this.id,
    required this.content,
    required this.isUser,
    required this.timestamp,
    this.reasoning,
    this.metadata,
  });

  factory MessageModel.fromJson(Map<String, dynamic> json) {
    return MessageModel(
      id: json['id'] as String,
      content: json['content'] as String,
      isUser: json['isUser'] as bool,
      timestamp: DateTime.parse(json['timestamp'] as String),
      reasoning: json['reasoning'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'isUser': isUser,
      'timestamp': timestamp.toIso8601String(),
      'reasoning': reasoning,
      'metadata': metadata,
    };
  }
}
