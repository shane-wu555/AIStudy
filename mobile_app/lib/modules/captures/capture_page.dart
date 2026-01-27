import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobile_app/widgets/three_d_visualization_widget.dart';
import 'capture_service.dart';
import 'models/guidance_flow.dart';
import 'models/guidance_step.dart';

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
  GuidanceFlow? _guidanceFlow;
  bool _isLoading = false;

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  /// 拍照采集
  Future<void> _capturePhoto() async {
    setState(() {
      _isLoading = true;
    });

    final guidance = await _captureService.capturePhotoAndGuide(
      userId: 'demo_user',
    );

    setState(() {
      _isLoading = false;
      _capturedImagePath = null;
      _guidanceFlow = guidance;
    });

    if (guidance != null) {
      _showSnackBar('已生成导学步骤');
    }
  }

  /// 从相册选择
  Future<void> _pickFromGallery() async {
    setState(() {
      _isLoading = true;
    });

    final guidance = await _captureService.pickFromGalleryAndGuide(
      userId: 'demo_user',
    );

    setState(() {
      _isLoading = false;
      _capturedImagePath = null;
      _guidanceFlow = guidance;
    });

    if (guidance != null) {
      _showSnackBar('已生成导学步骤');
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
      _onSubmitTextForGuidance(_textController.text);
    }
  }

  Future<void> _onSubmitTextForGuidance(String text) async {
    setState(() {
      _isLoading = true;
    });

    final guidance = await _captureService.submitTextForGuidance(
      userId: 'demo_user',
      text: text,
    );

    setState(() {
      _isLoading = false;
      _guidanceFlow = guidance;
    });

    _showSnackBar('已生成导学步骤');
    _textController.clear();
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
            if (_isLoading) const LinearProgressIndicator(minHeight: 2),
            if (_isLoading) const SizedBox(height: 8),
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
                    if (_guidanceFlow == null)
                      Container(
                        height: 80,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey.shade300),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          '拍照或选择图片后，系统会生成一步步的“导学流程”，\n帮助你理解题目，而不是直接给答案。',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey.shade700,
                          ),
                        ),
                      ),
                    if (_guidanceFlow != null) ...[
                      const SizedBox(height: 8),
                      _buildGuidanceSteps(),
                    ],
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

  Widget _buildGuidanceSteps() {
    final steps = _guidanceFlow?.steps ?? [];
    if (steps.isEmpty) {
      return Container();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '导学步骤',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: steps.length,
          separatorBuilder: (_, __) => const SizedBox(height: 8),
          itemBuilder: (context, index) {
            final step = steps[index];
            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                ListTile(
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  leading: CircleAvatar(
                    radius: 14,
                    backgroundColor: Colors.blue.shade50,
                    child: Text(
                      '${index + 1}',
                      style: const TextStyle(fontSize: 12, color: Colors.blue),
                    ),
                  ),
                  title: Text(
                    step.title,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: step.hint != null
                      ? Text(
                          step.hint!,
                          style: TextStyle(color: Colors.grey.shade700),
                        )
                      : null,
                  trailing: TextButton(
                    onPressed: () {
                      _followUpOnStep(step);
                    },
                    child: const Text('追问'),
                  ),
                ),
                if (step.geometry != null)
                  Padding(
                    padding: const EdgeInsets.only(
                      left: 16,
                      right: 16,
                      bottom: 4,
                    ),
                    child: SizedBox(
                      height: 160,
                      child: ThreeDVisualizationWidget(
                        visualizationType: 'geometry',
                        parameters: _normalizeGeometryParameters(step),
                        focusStepId: step.stepId,
                      ),
                    ),
                  ),
              ],
            );
          },
        ),
      ],
    );
  }

  Map<String, dynamic> _normalizeGeometryParameters(dynamic step) {
    final raw = step.geometry as Map<String, dynamic>;

    if (raw['objects'] is List) {
      // 如果后端已经返回标准结构，直接透传
      return raw;
    }

    // 否则，将单个几何对象包装成 objects 列表，并补充 step_id
    final enriched = Map<String, dynamic>.from(raw);
    enriched['step_id'] = step.stepId;

    return {
      'objects': [enriched],
    };
  }

  Future<void> _followUpOnStep(GuidanceStep step) async {
    final flow = _guidanceFlow;
    if (flow == null) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final newFlow = await _captureService.followUpOnStep(
        userId: 'demo_user',
        sessionId: flow.sessionId,
        stepId: step.stepId,
      );

      setState(() {
        _guidanceFlow = newFlow;
        _isLoading = false;
      });

      _showSnackBar('已根据步骤 ${step.stepId} 更新导学');
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      _showSnackBar('步骤追问失败，请稍后重试');
    }
  }
}
