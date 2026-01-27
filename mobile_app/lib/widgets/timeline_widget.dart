import 'package:flutter/material.dart';

/// 3D交互时间轴组件
/// 用于展示学习历程的可视化时间轴
class TimelineWidget extends StatefulWidget {
  final List<TimelineEvent> events;

  const TimelineWidget({Key? key, required this.events}) : super(key: key);

  @override
  State<TimelineWidget> createState() => _TimelineWidgetState();
}

class _TimelineWidgetState extends State<TimelineWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  int _selectedIndex = -1;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 200,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: widget.events.length,
        itemBuilder: (context, index) {
          final event = widget.events[index];
          final isSelected = _selectedIndex == index;

          return GestureDetector(
            onTap: () {
              setState(() {
                _selectedIndex = index;
              });
              _animationController.forward(from: 0);
            },
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              width: isSelected ? 140 : 100,
              margin: const EdgeInsets.symmetric(horizontal: 8),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // 事件图标
                  Container(
                    width: isSelected ? 70 : 50,
                    height: isSelected ? 70 : 50,
                    decoration: BoxDecoration(
                      color: event.color,
                      shape: BoxShape.circle,
                      boxShadow: isSelected
                          ? [
                              BoxShadow(
                                color: event.color.withOpacity(0.4),
                                blurRadius: 12,
                                spreadRadius: 2,
                              ),
                            ]
                          : null,
                    ),
                    child: Icon(
                      event.icon,
                      color: Colors.white,
                      size: isSelected ? 35 : 25,
                    ),
                  ),
                  const SizedBox(height: 8),

                  // 事件标题
                  Text(
                    event.title,
                    style: TextStyle(
                      fontSize: isSelected ? 14 : 12,
                      fontWeight: isSelected
                          ? FontWeight.bold
                          : FontWeight.normal,
                    ),
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),

                  // 时间标签
                  const SizedBox(height: 4),
                  Text(
                    event.timeLabel,
                    style: TextStyle(fontSize: 10, color: Colors.grey.shade600),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

/// 时间轴事件模型
class TimelineEvent {
  final String title;
  final String timeLabel;
  final IconData icon;
  final Color color;
  final DateTime timestamp;

  TimelineEvent({
    required this.title,
    required this.timeLabel,
    required this.icon,
    required this.color,
    required this.timestamp,
  });
}
