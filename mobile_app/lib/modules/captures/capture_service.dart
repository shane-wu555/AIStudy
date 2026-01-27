import 'package:image_picker/image_picker.dart';
import 'dart:io';

import '../../core/api_client.dart';
import 'models/guidance_flow.dart';

/// 采集服务类 - 处理多模态数据采集逻辑
class CaptureService {
  final ImagePicker _imagePicker = ImagePicker();
  final ApiClient _apiClient = ApiClient();

  // TODO: 集成语音录制库 (如 flutter_sound)
  // final FlutterSoundRecorder _recorder = FlutterSoundRecorder();

  /// 拍照采集，仅返回本地路径（底层能力）
  Future<String?> capturePhoto() async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (image != null) {
        return image.path;
      }
      return null;
    } catch (e) {
      print('拍照失败: $e');
      return null;
    }
  }

  /// 从相册选择，仅返回本地路径（底层能力）
  Future<String?> pickFromGallery() async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (image != null) {
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
      return 'audio_path';
    } catch (e) {
      print('停止录音失败: $e');
      return null;
    }
  }

  /// 提交文本（占位：仅打印）
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

  // ================== 导学流程相关（正式入口） ==================

  /// 拍照并发起导学流程：返回结构化的导学步骤，而不是长文本
  Future<GuidanceFlow?> capturePhotoAndGuide({
    required String userId,
    String? sessionId,
  }) async {
    final path = await capturePhoto();
    if (path == null) return null;
    return _uploadFileForGuidance(
      filePath: path,
      userId: userId,
      mode: 'image',
      sessionId: sessionId,
    );
  }

  /// 从相册选择并发起导学流程
  Future<GuidanceFlow?> pickFromGalleryAndGuide({
    required String userId,
    String? sessionId,
  }) async {
    final path = await pickFromGallery();
    if (path == null) return null;
    return _uploadFileForGuidance(
      filePath: path,
      userId: userId,
      mode: 'image',
      sessionId: sessionId,
    );
  }

  /// 提交语音录制结果并发起导学流程（当前音频路径为占位）
  Future<GuidanceFlow?> submitAudioForGuidance({
    required String userId,
    String? sessionId,
  }) async {
    final audioPath = await stopRecording();
    if (audioPath == null) return null;
    return _uploadFileForGuidance(
      filePath: audioPath,
      userId: userId,
      mode: 'audio',
      sessionId: sessionId,
    );
  }

  /// 直接提交文本，获取导学流程
  Future<GuidanceFlow> submitTextForGuidance({
    required String userId,
    required String text,
  }) async {
    try {
      final response = await _apiClient.post('/api/capture/text', {
        'user_id': userId,
        'content': text,
        'mode': 'text',
      });
      return GuidanceFlow.fromJson(response);
    } catch (e) {
      print('提交文本导学失败: $e');
      // 返回一个本地构造的导学流程，保证前端交互稳定
      return GuidanceFlow.fromJson({'content': text});
    }
  }

  /// 追问某一步骤（保留 step_id，便于后端做上下文追踪）
  Future<GuidanceFlow> followUpOnStep({
    required String userId,
    required String sessionId,
    required String stepId,
    String? question,
  }) async {
    try {
      final response = await _apiClient.post('/api/session/message', {
        'session_id': sessionId,
        'user_id': userId,
        'content': question ?? '我在步骤 $stepId 这里卡住了，帮我细化一下。',
        'step_id': stepId,
      });

      return GuidanceFlow.fromJson(response);
    } catch (e) {
      print('步骤追问失败: $e');
      return GuidanceFlow.fromJson({
        'session_id': sessionId,
        'content': question ?? '',
      });
    }
  }

  /// 实际的多模态文件上传，调用后端统一的 /upload/capture
  Future<GuidanceFlow?> _uploadFileForGuidance({
    required String filePath,
    required String userId,
    required String mode,
    String? sessionId,
  }) async {
    try {
      final response = await _apiClient.uploadFile(
        '/upload/capture',
        filePath,
        'file',
        fields: {
          'mode': mode,
          'user_id': userId,
          if (sessionId != null) 'session_id': sessionId,
        },
      );

      // 当前后端仅返回 task_id/status，这里用 GuidanceFlow 做一层兼容封装
      return GuidanceFlow.fromJson(response);
    } catch (e) {
      print('多模态上传失败: $e');
      return null;
    }
  }
}
