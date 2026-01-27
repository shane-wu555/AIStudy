import 'package:flutter/material.dart';
import 'dart:math' as math;

/// 3D可视化渲染组件
/// 用于展示数学概念、几何图形等的3D可视化
class ThreeDVisualizationWidget extends StatefulWidget {
  final String visualizationType; // 'geometry', 'function', 'vector'
  /// 后端返回的参数，例如：
  /// {
  ///   "objects": [
  ///     {"type": "line", "coords": [[0,0,0],[1,1,1]], "label": "辅助线 AC"}
  ///   ]
  /// }
  final Map<String, dynamic> parameters;

  /// 可选：只渲染属于某个导学步骤的几何对象（需要对象里带 step_id）
  final String? focusStepId;

  const ThreeDVisualizationWidget({
    Key? key,
    required this.visualizationType,
    required this.parameters,
    this.focusStepId,
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
                focusStepId: widget.focusStepId,
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
  final String? focusStepId;

  _ThreeDPainter({
    required this.visualizationType,
    required this.parameters,
    required this.rotationX,
    required this.rotationY,
    required this.focusStepId,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    final center = Offset(size.width / 2, size.height / 2);

    switch (visualizationType) {
      case 'geometry':
        _drawGeometryFromData(canvas, size, center, paint);
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

  Offset _projectPoint(double x, double y, double z, Offset center) {
    const scale = 100.0;
    double px = x * scale;
    double py = y * scale;
    double pz = z * scale;

    // 绕 Y 轴旋转
    final rx = px * math.cos(rotationY) - pz * math.sin(rotationY);
    final rz = px * math.sin(rotationY) + pz * math.cos(rotationY);

    // 绕 X 轴旋转
    final ry = py * math.cos(rotationX) - rz * math.sin(rotationX);

    return Offset(center.dx + rx, center.dy + ry);
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
    final projected = vertices
        .map(
          (v) => _projectPoint(
            v[0].toDouble(),
            v[1].toDouble(),
            v[2].toDouble(),
            center,
          ),
        )
        .toList();

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

  /// 根据后端返回的几何顶点数据绘制图形
  /// 示例：{"type": "line", "coords": [[0,0,0],[1,1,1]], "label": "辅助线 AC"}
  void _drawGeometryFromData(
    Canvas canvas,
    Size size,
    Offset center,
    Paint basePaint,
  ) {
    final objects = parameters['objects'] as List<dynamic>?;
    if (objects == null || objects.isEmpty) {
      // 无数据时，退回到立方体占位效果
      _drawCube(canvas, center, basePaint);
      return;
    }

    // 轻微网格背景，辅助空间感
    _drawGrid(canvas, size, center);

    for (final raw in objects) {
      if (raw is! Map<String, dynamic>) continue;
      // 如果指定了 focusStepId，则仅渲染匹配该 step 的对象
      if (focusStepId != null) {
        final objStepId = raw['step_id']?.toString();
        if (objStepId != null && objStepId != focusStepId) {
          continue;
        }
      }

      final type = raw['type']?.toString() ?? 'line';
      final coords = raw['coords'] as List<dynamic>?;
      if (coords == null || coords.length < 2) continue;

      final points = <Offset>[];
      for (final c in coords) {
        if (c is List && c.length >= 3) {
          final x = (c[0] as num).toDouble();
          final y = (c[1] as num).toDouble();
          final z = (c[2] as num).toDouble();
          points.add(_projectPoint(x, y, z, center));
        }
      }
      if (points.length < 2) continue;

      final globalLabel = parameters['label']?.toString();
      final objectLabel = raw['label']?.toString() ?? globalLabel;

      // 支持多条辅助线 + 点 + 面
      if (type == 'point') {
        _drawPoint(canvas, points.first, objectLabel);
      } else if (type == 'polygon' || type == 'face') {
        _drawFace(canvas, points, objectLabel);
      } else if (type == 'line') {
        _drawPolyline(canvas, points, objectLabel);
      } else {
        // 其他类型默认按折线处理
        _drawPolyline(canvas, points, objectLabel);
      }
    }
  }

  void _drawPolyline(Canvas canvas, List<Offset> points, String? label) {
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5
      ..color = Colors.blueAccent;

    for (var i = 0; i < points.length - 1; i++) {
      canvas.drawLine(points[i], points[i + 1], paint);
    }

    _drawLabel(canvas, points, Colors.blueAccent, label);
  }

  void _drawPoint(Canvas canvas, Offset point, String? label) {
    final fillPaint = Paint()
      ..style = PaintingStyle.fill
      ..color = Colors.redAccent;
    final borderPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2
      ..color = Colors.white;

    canvas.drawCircle(point, 5, fillPaint);
    canvas.drawCircle(point, 7, borderPaint);

    _drawLabel(canvas, [point], Colors.redAccent, label);
  }

  void _drawFace(Canvas canvas, List<Offset> points, String? label) {
    if (points.length < 3) {
      _drawPolyline(canvas, points, label);
      return;
    }

    final path = Path()..moveTo(points.first.dx, points.first.dy);
    for (var i = 1; i < points.length; i++) {
      path.lineTo(points[i].dx, points[i].dy);
    }
    path.close();

    final fillColor = Colors.orangeAccent.withOpacity(0.25);
    final borderColor = Colors.orangeAccent;

    final fillPaint = Paint()
      ..style = PaintingStyle.fill
      ..color = fillColor;
    final borderPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2
      ..color = borderColor;

    canvas.drawPath(path, fillPaint);
    canvas.drawPath(path, borderPaint);

    _drawLabel(canvas, points, borderColor, label);
  }

  void _drawLabel(
    Canvas canvas,
    List<Offset> points,
    Color color,
    String? label,
  ) {
    if (label == null || label.isEmpty) {
      return;
    }

    final midIndex = (points.length / 2).floor();
    final midPoint = points[midIndex];

    final textPainter = TextPainter(
      text: TextSpan(
        text: label,
        style: TextStyle(fontSize: 12, color: color.withOpacity(0.9)),
      ),
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(midPoint.dx + 6, midPoint.dy - textPainter.height / 2),
    );
  }

  void _drawGrid(Canvas canvas, Size size, Offset center) {
    final gridPaint = Paint()
      ..color = Colors.grey.withOpacity(0.15)
      ..strokeWidth = 1;

    const step = 30.0;
    for (double x = 0; x <= size.width; x += step) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), gridPaint);
    }
    for (double y = 0; y <= size.height; y += step) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
    }

    final axisPaint = Paint()
      ..color = Colors.grey.withOpacity(0.4)
      ..strokeWidth = 2;
    canvas.drawLine(
      Offset(0, center.dy),
      Offset(size.width, center.dy),
      axisPaint,
    );
    canvas.drawLine(
      Offset(center.dx, 0),
      Offset(center.dx, size.height),
      axisPaint,
    );
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
