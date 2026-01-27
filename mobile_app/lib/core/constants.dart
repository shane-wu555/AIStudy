/// 应用常量配置
class AppConstants {
  // API配置
  static const String apiBaseUrl = 'http://localhost:8000';
  static const String wsBaseUrl = 'ws://localhost:8000';

  // 超时配置
  static const Duration apiTimeout = Duration(seconds: 30);
  static const Duration wsTimeout = Duration(seconds: 5);

  // 缓存配置
  static const int maxCacheSize = 100 * 1024 * 1024; // 100MB
  static const Duration cacheExpiration = Duration(hours: 24);

  // 图片配置
  static const int maxImageWidth = 1920;
  static const int maxImageHeight = 1080;
  static const int imageQuality = 85;

  // 语音配置
  static const int maxRecordingDuration = 180; // 3分钟
  static const String audioFormat = 'aac';

  // 分页配置
  static const int defaultPageSize = 20;

  // UI配置
  static const double defaultPadding = 16.0;
  static const double defaultRadius = 12.0;
}

/// 应用路由
class AppRoutes {
  static const String home = '/';
  static const String capture = '/capture';
  static const String session = '/session';
  static const String records = '/records';
  static const String settings = '/settings';
}
