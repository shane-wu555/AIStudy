import 'package:flutter/material.dart';
import 'session_service.dart';
import 'models/message_model.dart';

/// 导学会话展示区 - UC04 智能导学对话
/// 展示AI导学的多轮对话，支持追问和上下文管理
class SessionPage extends StatefulWidget {
  const SessionPage({Key? key}) : super(key: key);

  @override
  State<SessionPage> createState() => _SessionPageState();
}

class _SessionPageState extends State<SessionPage> {
  final SessionService _sessionService = SessionService();
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  List<MessageModel> _messages = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadSession();
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  /// 加载会话历史
  Future<void> _loadSession() async {
    setState(() {
      _isLoading = true;
    });

    final messages = await _sessionService.loadSessionHistory();

    setState(() {
      _messages = messages;
      _isLoading = false;
    });

    _scrollToBottom();
  }

  /// 发送消息
  Future<void> _sendMessage() async {
    if (_messageController.text.trim().isEmpty) return;

    final userMessage = MessageModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: _messageController.text,
      isUser: true,
      timestamp: DateTime.now(),
    );

    setState(() {
      _messages.add(userMessage);
      _isLoading = true;
    });

    _messageController.clear();
    _scrollToBottom();

    // 调用AI服务获取回复
    final aiResponse = await _sessionService.sendMessage(userMessage.content);

    setState(() {
      _messages.add(aiResponse);
      _isLoading = false;
    });

    _scrollToBottom();
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI导学助手'),
        backgroundColor: Colors.blue,
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: () {
              // 清空会话
              setState(() {
                _messages.clear();
              });
              _sessionService.clearSession();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // 会话上下文提示
          Container(
            padding: const EdgeInsets.all(8.0),
            color: Colors.blue.shade50,
            child: Row(
              children: [
                const Icon(Icons.info_outline, size: 16, color: Colors.blue),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '支持多轮对话和追问，AI会记住上下文',
                    style: TextStyle(fontSize: 12, color: Colors.blue.shade700),
                  ),
                ),
              ],
            ),
          ),

          // 消息列表
          Expanded(
            child: _isLoading && _messages.isEmpty
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      final message = _messages[index];
                      return _buildMessageBubble(message);
                    },
                  ),
          ),

          // 输入区域
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.3),
                  blurRadius: 4,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: const InputDecoration(
                      hintText: '输入您的问题...',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                    ),
                    maxLines: null,
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8),
                FloatingActionButton(
                  onPressed: _isLoading ? null : _sendMessage,
                  child: _isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.send),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(MessageModel message) {
    return Align(
      alignment: message.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.all(12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: message.isUser ? Colors.blue : Colors.grey.shade200,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message.content,
              style: TextStyle(
                color: message.isUser ? Colors.white : Colors.black87,
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              _formatTime(message.timestamp),
              style: TextStyle(
                color: message.isUser ? Colors.white70 : Colors.grey.shade600,
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}
