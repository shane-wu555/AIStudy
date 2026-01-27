import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'modules/captures/capture_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Numbers Fall Into Place',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const CapturePage(),
    );
  }
}

class CapturePage extends StatefulWidget {
  const CapturePage({super.key});

  @override
  State<CapturePage> createState() => _CapturePageState();
}

class _CapturePageState extends State<CapturePage> {
  final CaptureService _service = CaptureService();
  final ImagePicker _picker = ImagePicker();
  bool _isUploading = false;
  String _message = '';

  Future<void> _pickFromGalleryAndUpload() async {
    setState(() {
      _message = '';
    });

    // 1. 打开相册选择图片
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);

    if (image == null) {
      setState(() {
        _message = '已取消选择';
      });
      return;
    }

    const userId = 'test_user_001'; // TODO: 替换为真实用户 ID

    setState(() {
      _isUploading = true;
      _message = '正在上传：${image.name}';
    });

    try {
      await _service.uploadMathProblem(image.path, userId);
      setState(() {
        _message = '上传完成：${image.name}';
      });
    } catch (e) {
      setState(() {
        _message = '上传出错: $e';
      });
    } finally {
      setState(() {
        _isUploading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Capture Service Demo'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ElevatedButton(
              onPressed: _isUploading ? null : _pickFromGalleryAndUpload,
              child: Text(_isUploading ? '上传中...' : '从相册选择题目图片并上传'),
            ),
            const SizedBox(height: 16),
            Text(
              _message,
              style: const TextStyle(fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }
}
