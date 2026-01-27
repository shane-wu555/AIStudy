import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'capture_service.dart';

/// 拍照/语音/文本采集模块 - UC03 多模态采集
/// 支持拍照、语音录制、文本输入三种方式
class CapturePage extends StatefulWidget {
  const CapturePage({Key? key}) : super(key: key);

  @override
  State<CapturePage> createState() => _CapturePageState();
}

class _CapturePageState extends State<CapturePage> {
  final CaptureService _captureService = CaptureService();
  final TextEditingController _textController = TextEditingController();

  bool _isRecording = false;
  String? _capturedImagePath;

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  /// 拍照采集
  Future<void> _capturePhoto() async {
    final imagePath = await _captureService.capturePhoto();
    if (imagePath != null) {
      setState(() {
        _capturedImagePath = imagePath;
      });
      _showSnackBar('照片已采集');
    }
  }

  /// 从相册选择
  Future<void> _pickFromGallery() async {
    final imagePath = await _captureService.pickFromGallery();
    if (imagePath != null) {
      setState(() {
        _capturedImagePath = imagePath;
      });
      _showSnackBar('图片已选择');
    }
  }

  /// 语音录制
  Future<void> _toggleVoiceRecording() async {
    if (_isRecording) {
      final audioPath = await _captureService.stopRecording();
      if (audioPath != null) {
        _showSnackBar('语音录制完成');
      }
      setState(() {
        _isRecording = false;
      });
    } else {
      final success = await _captureService.startRecording();
      if (success) {
        setState(() {
          _isRecording = true;
        });
        _showSnackBar('开始录音...');
      }
    }
  }

  /// 提交文本
  void _submitText() {
    if (_textController.text.isNotEmpty) {
      _captureService.submitText(_textController.text);
      _showSnackBar('文本已提交');
      _textController.clear();
    }
  }

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('多模态采集'), backgroundColor: Colors.blue),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 图像采集区域
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    const Text(
                      '图像采集',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    if (_capturedImagePath != null)
                      Container(
                        height: 200,
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Center(
                          child: Icon(Icons.image, size: 100),
                        ),
                      ),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        ElevatedButton.icon(
                          onPressed: _capturePhoto,
                          icon: const Icon(Icons.camera_alt),
                          label: const Text('拍照'),
                        ),
                        ElevatedButton.icon(
                          onPressed: _pickFromGallery,
                          icon: const Icon(Icons.photo_library),
                          label: const Text('相册'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // 语音采集区域
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    const Text(
                      '语音采集',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: _toggleVoiceRecording,
                      icon: Icon(_isRecording ? Icons.stop : Icons.mic),
                      label: Text(_isRecording ? '停止录音' : '开始录音'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _isRecording
                            ? Colors.red
                            : Colors.blue,
                        minimumSize: const Size(200, 50),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // 文本输入区域
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    const Text(
                      '文本输入',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _textController,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        hintText: '请输入您的问题或描述...',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: _submitText,
                      icon: const Icon(Icons.send),
                      label: const Text('提交'),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
