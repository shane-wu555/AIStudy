import 'package:flutter/material.dart';
import 'package:mobile_app/widgets/timeline_widget.dart';
import 'package:mobile_app/widgets/three_d_visualization_widget.dart';
import 'records_service.dart';
import 'models/learning_record.dart';

/// 学习记录回顾 - UC06 学习轨迹管理
/// 展示学习历史、统计数据、进度追踪
class RecordsPage extends StatefulWidget {
  const RecordsPage({Key? key}) : super(key: key);

  @override
  State<RecordsPage> createState() => _RecordsPageState();
}

class _RecordsPageState extends State<RecordsPage>
    with SingleTickerProviderStateMixin {
  final RecordsService _recordsService = RecordsService();

  late TabController _tabController;
  List<LearningRecord> _records = [];
  Map<String, dynamic> _statistics = {};
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadRecords();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadRecords() async {
    setState(() {
      _isLoading = true;
    });

    final records = await _recordsService.getRecords();
    final stats = await _recordsService.getStatistics();

    setState(() {
      _records = records;
      _statistics = stats;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('学习记录'),
        backgroundColor: Colors.blue,
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.history), text: '历史记录'),
            Tab(icon: Icon(Icons.analytics), text: '统计分析'),
            Tab(icon: Icon(Icons.timeline), text: '学习轨迹'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _buildHistoryTab(),
                _buildStatisticsTab(),
                _buildTimelineTab(),
              ],
            ),
    );
  }

  /// 历史记录标签页
  Widget _buildHistoryTab() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _records.length,
      itemBuilder: (context, index) {
        final record = _records[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: _getColorByType(record.type),
              child: Icon(_getIconByType(record.type), color: Colors.white),
            ),
            title: Text(record.title),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(record.description),
                const SizedBox(height: 4),
                Text(
                  _formatDate(record.timestamp),
                  style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                ),
              ],
            ),
            trailing: IconButton(
              icon: const Icon(Icons.arrow_forward_ios, size: 16),
              onPressed: () {
                // 查看详情
                _showRecordDetail(record);
              },
            ),
          ),
        );
      },
    );
  }

  /// 统计分析标签页
  Widget _buildStatisticsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildStatCard(
            '学习天数',
            '${_statistics['studyDays'] ?? 0}',
            Icons.calendar_today,
            Colors.blue,
          ),
          const SizedBox(height: 12),
          _buildStatCard(
            '总学习时长',
            '${_statistics['totalHours'] ?? 0} 小时',
            Icons.access_time,
            Colors.green,
          ),
          const SizedBox(height: 12),
          _buildStatCard(
            '完成题目',
            '${_statistics['completedProblems'] ?? 0} 题',
            Icons.check_circle,
            Colors.orange,
          ),
          const SizedBox(height: 12),
          _buildStatCard(
            '知识点掌握',
            '${_statistics['masteredTopics'] ?? 0} 个',
            Icons.lightbulb,
            Colors.purple,
          ),
          const SizedBox(height: 24),

          // 进度图表占位
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  const Text(
                    '学习进度趋势',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  Container(
                    height: 200,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey.shade300),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Center(child: Text('TODO: 集成图表库展示学习趋势')),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 学习轨迹标签页
  Widget _buildTimelineTab() {
    if (_records.isEmpty) {
      return const Center(child: Text('暂无学习记录'));
    }

    // 将学习记录映射到时间轴事件
    final events =
        _records
            .map(
              (record) => TimelineEvent(
                title: record.title,
                timeLabel: _formatDate(record.timestamp),
                icon: _getIconByType(record.type),
                color: _getColorByType(record.type),
                timestamp: record.timestamp,
              ),
            )
            .toList()
          ..sort((a, b) => a.timestamp.compareTo(b.timestamp));

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // 顶部时间轴总览（横向3D时间轴组件）
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '学习轨迹时间轴',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(height: 200, child: TimelineWidget(events: events)),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // 简单的 3D 概念可视化（当前为占位实现）
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text(
                    '学习概念 3D 预览',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 12),
                  SizedBox(
                    height: 220,
                    child: ThreeDVisualizationWidget(
                      visualizationType: 'geometry',
                      parameters: <String, dynamic>{
                        'objects': [
                          {
                            'type': 'line',
                            'coords': [
                              [0.0, 0.0, 0.0],
                              [1.0, 1.0, 1.0],
                            ],
                            'label': '辅助线 AC',
                          },
                        ],
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // 详细的纵向时间线列表（保留原来的详细信息）
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _records.length,
            itemBuilder: (context, index) {
              final record = _records[index];
              final isLast = index == _records.length - 1;

              return IntrinsicHeight(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 时间轴节点
                    Column(
                      children: [
                        Container(
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            color: _getColorByType(record.type),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            _getIconByType(record.type),
                            color: Colors.white,
                            size: 20,
                          ),
                        ),
                        if (!isLast)
                          Expanded(
                            child: Container(
                              width: 2,
                              color: Colors.grey.shade300,
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(width: 16),

                    // 记录内容
                    Expanded(
                      child: Card(
                        margin: const EdgeInsets.only(bottom: 16),
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                record.title,
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(record.description),
                              const SizedBox(height: 8),
                              Text(
                                _formatDate(record.timestamp),
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              width: 50,
              height: 50,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: TextStyle(fontSize: 14, color: Colors.grey.shade600),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    value,
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getColorByType(String type) {
    switch (type) {
      case 'question':
        return Colors.blue;
      case 'practice':
        return Colors.green;
      case 'review':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  IconData _getIconByType(String type) {
    switch (type) {
      case 'question':
        return Icons.quiz;
      case 'practice':
        return Icons.edit;
      case 'review':
        return Icons.replay;
      default:
        return Icons.circle;
    }
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inDays == 0) {
      return '今天 ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
    } else if (diff.inDays == 1) {
      return '昨天 ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
    } else {
      return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
    }
  }

  void _showRecordDetail(LearningRecord record) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(record.title),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(record.description),
            const SizedBox(height: 16),
            Text('类型: ${record.type}'),
            Text('时间: ${_formatDate(record.timestamp)}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('关闭'),
          ),
        ],
      ),
    );
  }
}
