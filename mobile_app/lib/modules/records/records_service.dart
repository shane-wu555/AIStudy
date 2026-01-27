import 'models/learning_record.dart';
import '../../core/api_client.dart';

/// 学习记录服务
class RecordsService {
  final ApiClient _apiClient = ApiClient();

  /// 获取学习记录列表
  Future<List<LearningRecord>> getRecords() async {
    try {
      // TODO: 从后端API获取
      // final response = await _apiClient.get('/api/records');

      // 模拟数据
      return [
        LearningRecord(
          id: '1',
          title: '解决了一道数学题',
          description: '关于二次方程的求解',
          type: 'practice',
          timestamp: DateTime.now().subtract(const Duration(hours: 2)),
        ),
        LearningRecord(
          id: '2',
          title: '提问了物理问题',
          description: '牛顿第二定律的应用',
          type: 'question',
          timestamp: DateTime.now().subtract(const Duration(days: 1)),
        ),
        LearningRecord(
          id: '3',
          title: '复习了化学知识',
          description: '元素周期表记忆',
          type: 'review',
          timestamp: DateTime.now().subtract(const Duration(days: 2)),
        ),
      ];
    } catch (e) {
      print('获取学习记录失败: $e');
      return [];
    }
  }

  /// 获取统计数据
  Future<Map<String, dynamic>> getStatistics() async {
    try {
      // TODO: 从后端API获取
      // final response = await _apiClient.get('/api/records/statistics');

      // 模拟数据
      return {
        'studyDays': 15,
        'totalHours': 48,
        'completedProblems': 127,
        'masteredTopics': 23,
      };
    } catch (e) {
      print('获取统计数据失败: $e');
      return {};
    }
  }

  /// 添加学习记录
  Future<bool> addRecord(LearningRecord record) async {
    try {
      // TODO: 调用后端API
      // await _apiClient.post('/api/records', record.toJson());
      return true;
    } catch (e) {
      print('添加学习记录失败: $e');
      return false;
    }
  }
}
