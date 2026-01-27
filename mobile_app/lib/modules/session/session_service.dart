import 'dart:convert';
import 'models/message_model.dart';
import '../../core/api_client.dart';

/// 会话服务 - 管理导学对话的业务逻辑
class SessionService {
  final ApiClient _apiClient = ApiClient();
  String? _currentSessionId;

  /// 加载会话历史
  Future<List<MessageModel>> loadSessionHistory() async {
    try {
      // TODO: 从后端API获取会话历史
      // final response = await _apiClient.get('/api/session/history');

      // 模拟数据
      return [
        MessageModel(
          id: '1',
          content: '您好！我是AI导学助手，有什么可以帮您的吗？',
          isUser: false,
          timestamp: DateTime.now().subtract(const Duration(minutes: 5)),
        ),
      ];
    } catch (e) {
      print('加载会话历史失败: $e');
      return [];
    }
  }

  /// 发送消息并获取AI回复
  Future<MessageModel> sendMessage(String content) async {
    try {
      // TODO: 调用后端WebSocket或RESTful API
      // final response = await _apiClient.post('/api/session/message', {
      //   'sessionId': _currentSessionId,
      //   'content': content,
      // });

      // 模拟AI回复
      await Future.delayed(const Duration(seconds: 1));

      return MessageModel(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        content: '这是一个模拟回复。实际应用中，这里会调用后端AI服务进行推理。',
        isUser: false,
        timestamp: DateTime.now(),
        reasoning: '推理链路：问题理解 → 知识检索 → 答案生成',
      );
    } catch (e) {
      print('发送消息失败: $e');
      return MessageModel(
        id: 'error',
        content: '抱歉，服务暂时不可用，请稍后重试。',
        isUser: false,
        timestamp: DateTime.now(),
      );
    }
  }

  /// 清空当前会话
  Future<void> clearSession() async {
    try {
      // TODO: 调用后端API清空会话
      _currentSessionId = null;
    } catch (e) {
      print('清空会话失败: $e');
    }
  }

  /// 获取会话上下文
  Future<Map<String, dynamic>> getSessionContext() async {
    try {
      // TODO: 获取当前会话的上下文信息
      return {'sessionId': _currentSessionId, 'messageCount': 0, 'topics': []};
    } catch (e) {
      print('获取会话上下文失败: $e');
      return {};
    }
  }
}
