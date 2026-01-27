import 'package:flutter/material.dart';

/// 知识点卡片组件
/// 用于展示知识点详情
class KnowledgeCardWidget extends StatelessWidget {
  final String title;
  final String content;
  final List<String> relatedTopics;
  final VoidCallback? onTap;

  const KnowledgeCardWidget({
    Key? key,
    required this.title,
    required this.content,
    this.relatedTopics = const [],
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 3,
      margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 标题
              Row(
                children: [
                  Icon(Icons.lightbulb_outline, color: Colors.amber.shade700),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      title,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              const Divider(height: 24),

              // 内容
              Text(content, style: const TextStyle(fontSize: 15, height: 1.5)),

              // 相关知识点
              if (relatedTopics.isNotEmpty) ...[
                const SizedBox(height: 16),
                const Text(
                  '相关知识点:',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: relatedTopics.map((topic) {
                    return Chip(
                      label: Text(topic, style: const TextStyle(fontSize: 12)),
                      backgroundColor: Colors.blue.shade50,
                      padding: const EdgeInsets.symmetric(horizontal: 8),
                    );
                  }).toList(),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
