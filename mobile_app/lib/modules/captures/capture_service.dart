import 'package:image_picker/image_picker.dart';
import 'dart:io';

/// 采集服务类 - 处理多模态数据采集逻辑
class CaptureService {
  final ImagePicker _imagePicker = ImagePicker();

  // TODO: 集成语音录制库 (如 flutter_sound)
  // final FlutterSoundRecorder _recorder = FlutterSoundRecorder();

  /// 拍照采集
  Future<String?> capturePhoto() async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (image != null) {
        // TODO: 上传到后端服务
        return image.path;
      }
      return null;
    } catch (e) {
      print('拍照失败: $e');
      return null;
    }
  }

  /// 从相册选择
  Future<String?> pickFromGallery() async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (image != null) {
        // TODO: 上传到后端服务
        return image.path;
      }
      return null;
    } catch (e) {
      print('选择图片失败: $e');
      return null;
    }
  }

  /// 开始录音
  Future<bool> startRecording() async {
    try {
      // TODO: 实现语音录制
      // await _recorder.startRecorder(toFile: 'audio.aac');
      return true;
    } catch (e) {
      print('开始录音失败: $e');
      return false;
    }
  }

  /// 停止录音
  Future<String?> stopRecording() async {
    try {
      // TODO: 实现语音录制
      // final path = await _recorder.stopRecorder();
      // 上传到后端服务
      return 'audio_path';
    } catch (e) {
      print('停止录音失败: $e');
      return null;
    }
  }

  /// 提交文本
  Future<void> submitText(String text) async {
    try {
      // TODO: 发送到后端API
      print('提交文本: $text');
    } catch (e) {
      print('提交文本失败: $e');
    }
  }

  /// 兼容旧 Demo：上传数学题图片
  /// 当前为占位实现，只做本地检查和延时模拟
  Future<void> uploadMathProblem(String imagePath, String userId) async {
    try {
      final file = File(imagePath);
      if (!file.existsSync()) {
        throw Exception('图片文件不存在');
      }

      // TODO: 在这里集成真正的上传逻辑（调用后端 /api/capture/image）
      print('模拟上传数学题图片: path=$imagePath, user=$userId');
      await Future.delayed(const Duration(seconds: 1));
    } catch (e) {
      print('上传数学题失败: $e');
      rethrow;
    }
  }
}
