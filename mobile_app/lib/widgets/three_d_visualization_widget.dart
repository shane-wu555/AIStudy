import 'package:flutter/material.dart';
import 'dart:math' as math;

/// 3D可视化渲染组件
/// 用于展示数学概念、几何图形等的3D可视化
class ThreeDVisualizationWidget extends StatefulWidget {
  final String visualizationType; // 'geometry', 'function', 'vector'
  final Map<String, dynamic> parameters;

  const ThreeDVisualizationWidget({
    Key? key,
    required this.visualizationType,
    required this.parameters,
  }) : super(key: key);

  @override
  State<ThreeDVisualizationWidget> createState() =>
      _ThreeDVisualizationWidgetState();
}

class _ThreeDVisualizationWidgetState extends State<ThreeDVisualizationWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _rotationController;
  double _rotationX = 0;
  double _rotationY = 0;
  Offset? _lastPanPosition;

  @override
  void initState() {
    super.initState();
    _rotationController = AnimationController(
      duration: const Duration(seconds: 10),
      vsync: this,
    )..repeat();
  }

  @override
  void dispose() {
    _rotationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: GestureDetector(
        onPanStart: (details) {
          _lastPanPosition = details.localPosition;
          _rotationController.stop();
        },
        onPanUpdate: (details) {
          setState(() {
            final delta = details.localPosition - _lastPanPosition!;
            _rotationX += delta.dy * 0.01;
            _rotationY += delta.dx * 0.01;
            _lastPanPosition = details.localPosition;
          });
        },
        onPanEnd: (_) {
          _rotationController.repeat();
        },
        child: AnimatedBuilder(
          animation: _rotationController,
          builder: (context, child) {
            return CustomPaint(
              painter: _ThreeDPainter(
                visualizationType: widget.visualizationType,
                parameters: widget.parameters,
                rotationX: _rotationX,
                rotationY: _rotationY + _rotationController.value * 2 * math.pi,
              ),
              child: Container(),
            );
          },
        ),
      ),
    );
  }
}

/// 3D绘制器
class _ThreeDPainter extends CustomPainter {
  final String visualizationType;
  final Map<String, dynamic> parameters;
  final double rotationX;
  final double rotationY;

  _ThreeDPainter({
    required this.visualizationType,
    required this.parameters,
    required this.rotationX,
    required this.rotationY,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    final center = Offset(size.width / 2, size.height / 2);

    // TODO: 实现真正的3D渲染逻辑
    // 这里提供一个简化的立方体示例
    switch (visualizationType) {
      case 'geometry':
        _drawCube(canvas, center, paint);
        break;
      case 'function':
        _drawFunction(canvas, size, paint);
        break;
      case 'vector':
        _drawVector(canvas, center, paint);
        break;
      default:
        _drawPlaceholder(canvas, center);
    }
  }

  void _drawCube(Canvas canvas, Offset center, Paint paint) {
    final size = 100.0;

    // 简化的立方体顶点
    final vertices = [
      [-1, -1, -1],
      [1, -1, -1],
      [1, 1, -1],
      [-1, 1, -1],
      [-1, -1, 1],
      [1, -1, 1],
      [1, 1, 1],
      [-1, 1, 1],
    ];

    // 应用旋转和投影
    final projected = vertices.map((v) {
      final x = v[0] * size;
      final y = v[1] * size;
      final z = v[2] * size;

      // 简化的投影（实际应用中应使用透视投影矩阵）
      final projX = x * math.cos(rotationY) - z * math.sin(rotationY);
      final projZ = x * math.sin(rotationY) + z * math.cos(rotationY);
      final projY = y * math.cos(rotationX) - projZ * math.sin(rotationX);

      return Offset(center.dx + projX, center.dy + projY);
    }).toList();

    // 绘制边
    final edges = [
      [0, 1], [1, 2], [2, 3], [3, 0], // 前面
      [4, 5], [5, 6], [6, 7], [7, 4], // 后面
      [0, 4], [1, 5], [2, 6], [3, 7], // 连接线
    ];

    for (var edge in edges) {
      canvas.drawLine(projected[edge[0]], projected[edge[1]], paint);
    }
  }

  void _drawFunction(Canvas canvas, Size size, Paint paint) {
    // 绘制函数图像的简化示例
    final path = Path();
    for (var i = 0; i < size.width; i += 2) {
      final x = (i - size.width / 2) / 50;
      final y = math.sin(x + rotationY) * 50;
      if (i == 0) {
        path.moveTo(i.toDouble(), size.height / 2 + y);
      } else {
        path.lineTo(i.toDouble(), size.height / 2 + y);
      }
    }
    canvas.drawPath(path, paint);
  }

  void _drawVector(Canvas canvas, Offset center, Paint paint) {
    // 绘制向量的简化示例
    final arrowPaint = Paint()
      ..color = Colors.red
      ..strokeWidth = 3.0
      ..style = PaintingStyle.stroke;

    final endX = center.dx + 100 * math.cos(rotationY);
    final endY = center.dy + 100 * math.sin(rotationX);

    canvas.drawLine(center, Offset(endX, endY), arrowPaint);

    // 绘制箭头
    final arrowSize = 15.0;
    final angle = math.atan2(endY - center.dy, endX - center.dx);

    canvas.drawLine(
      Offset(endX, endY),
      Offset(
        endX - arrowSize * math.cos(angle - 0.5),
        endY - arrowSize * math.sin(angle - 0.5),
      ),
      arrowPaint,
    );

    canvas.drawLine(
      Offset(endX, endY),
      Offset(
        endX - arrowSize * math.cos(angle + 0.5),
        endY - arrowSize * math.sin(angle + 0.5),
      ),
      arrowPaint,
    );
  }

  void _drawPlaceholder(Canvas canvas, Offset center) {
    final textPainter = TextPainter(
      text: TextSpan(
        text: '3D渲染区域\n(需集成three.dart或类似库)',
        style: TextStyle(color: Colors.grey.shade600, fontSize: 14),
      ),
      textDirection: TextDirection.ltr,
      textAlign: TextAlign.center,
    );
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(
        center.dx - textPainter.width / 2,
        center.dy - textPainter.height / 2,
      ),
    );
  }

  @override
  bool shouldRepaint(_ThreeDPainter oldDelegate) => true;
}
