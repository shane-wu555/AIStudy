import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

/// 本地存储服务
class StorageService {
  static SharedPreferences? _prefs;

  /// 初始化
  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  /// 保存字符串
  static Future<bool> saveString(String key, String value) async {
    return await _prefs?.setString(key, value) ?? false;
  }

  /// 获取字符串
  static String? getString(String key) {
    return _prefs?.getString(key);
  }

  /// 保存整数
  static Future<bool> saveInt(String key, int value) async {
    return await _prefs?.setInt(key, value) ?? false;
  }

  /// 获取整数
  static int? getInt(String key) {
    return _prefs?.getInt(key);
  }

  /// 保存布尔值
  static Future<bool> saveBool(String key, bool value) async {
    return await _prefs?.setBool(key, value) ?? false;
  }

  /// 获取布尔值
  static bool? getBool(String key) {
    return _prefs?.getBool(key);
  }

  /// 保存JSON对象
  static Future<bool> saveJson(String key, Map<String, dynamic> value) async {
    return await saveString(key, jsonEncode(value));
  }

  /// 获取JSON对象
  static Map<String, dynamic>? getJson(String key) {
    final str = getString(key);
    if (str == null) return null;
    try {
      return jsonDecode(str) as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }

  /// 删除键值
  static Future<bool> remove(String key) async {
    return await _prefs?.remove(key) ?? false;
  }

  /// 清空所有数据
  static Future<bool> clear() async {
    return await _prefs?.clear() ?? false;
  }

  /// 检查键是否存在
  static bool containsKey(String key) {
    return _prefs?.containsKey(key) ?? false;
  }
}

/// 存储键常量
class StorageKeys {
  static const String userId = 'user_id';
  static const String sessionId = 'session_id';
  static const String theme = 'theme';
  static const String language = 'language';
  static const String lastSync = 'last_sync';
}
