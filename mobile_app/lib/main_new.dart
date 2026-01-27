import 'package:flutter/material.dart';
import 'modules/captures/capture_page.dart';
import 'modules/session/session_page.dart';
import 'modules/records/records_page.dart';
import 'core/storage_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 初始化本地存储
  await StorageService.init();

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NumbersFallIntoPlace',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const HomePage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _currentIndex = 0;

  final List<Widget> _pages = [
    const CenterPage(),
    const CapturePage(),
    const SessionPage(),
    const RecordsPage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: '首页'),
          BottomNavigationBarItem(icon: Icon(Icons.camera_alt), label: '采集'),
          BottomNavigationBarItem(icon: Icon(Icons.chat), label: '对话'),
          BottomNavigationBarItem(icon: Icon(Icons.history), label: '记录'),
        ],
      ),
    );
  }
}

class CenterPage extends StatelessWidget {
  const CenterPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('NumbersFallIntoPlace'),
        backgroundColor: Colors.blue,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.school, size: 100, color: Colors.blue.shade300),
            const SizedBox(height: 24),
            const Text(
              '智能教育AI助手',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: Text(
                '支持拍照、语音、文本多模态输入\n智能导学对话，学习轨迹管理',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey.shade600,
                  height: 1.5,
                ),
              ),
            ),
            const SizedBox(height: 48),
            ElevatedButton.icon(
              onPressed: () {
                // 快速开始
              },
              icon: const Icon(Icons.play_arrow),
              label: const Text('开始使用'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  horizontal: 32,
                  vertical: 16,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
