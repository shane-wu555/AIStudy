# NumbersFallIntoPlace - 智能教育AI助手

## 项目简介

NumbersFallIntoPlace 是一个基于AI的智能教育助手应用，支持多模态输入（拍照、语音、文本），提供智能导学对话和学习轨迹管理功能。

## 架构概览

```
NumbersFallIntoPlace/
├── mobile_app/                # Flutter移动端
│   ├── lib/
│   │   ├── modules/          # 功能模块
│   │   │   ├── captures/     # 拍照/语音/文本采集
│   │   │   ├── session/      # 导学会话展示
│   │   │   └── records/      # 学习记录回顾
│   │   ├── widgets/          # 自定义组件
│   │   └── core/             # 核心工具
│   └── pubspec.yaml
│
├── backend_service/          # 后端服务 (FastAPI)
│   ├── api/                  # REST/WebSocket接口
│   ├── service/              # 业务逻辑层
│   ├── model_interface/      # AI模型调用抽象
│   ├── utils/                # 多模态数据处理
│   └── main.py
│
├── ai_engine/                # AI推理引擎
│   ├── multimodal_parser/    # 多模态理解
│   ├── reasoning_chain/      # 可追问推理链
│   ├── knowledge_base/       # 知识库管理
│   └── main.py
│
└── scripts/                  # 部署脚本
    ├── deploy_backend.sh
    ├── deploy_ai_engine.sh
    └── build_mobile.sh
```

## 主要功能

### 1. 多模态采集 (UC03)
- 📷 拍照题目识别
- 🎤 语音问题输入
- ⌨️ 文本直接输入

### 2. 智能导学对话 (UC04)
- 💬 多轮对话支持
- 🔄 上下文管理
- 🧠 可追问推理链

### 3. 学习记录管理 (UC06)
- 📊 学习统计分析
- 📈 进度可视化
- ⏱️ 学习轨迹时间轴

## 快速开始

### 环境要求

**移动端:**
- Flutter SDK >= 3.0.0
- Dart >= 3.0.0

**后端:**
- Python >= 3.9
- FastAPI
- Uvicorn

**AI引擎:**
- Python >= 3.9
- PyTorch (可选)
- Transformers (可选)

### 安装步骤

#### 1. 移动端

```bash
cd mobile_app
flutter pub get
flutter run
```

#### 2. 后端服务

```bash
cd backend_service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

服务将在 http://localhost:8000 启动
API文档: http://localhost:8000/docs

#### 3. AI引擎

```bash
cd ai_engine
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

服务将在 http://localhost:8001 启动

### 使用部署脚本

**Linux/Mac:**
```bash
chmod +x scripts/*.sh
./scripts/deploy_backend.sh
./scripts/deploy_ai_engine.sh
./scripts/build_mobile.sh
```

**Windows:**
```powershell
.\scripts\deploy_backend.ps1
```

## API接口

### 后端服务 (port 8000)

#### 采集接口
- `POST /api/capture/text` - 文本采集
- `POST /api/capture/image` - 图像采集
- `POST /api/capture/audio` - 语音采集

#### 会话接口
- `POST /api/session/message` - 发送消息
- `GET /api/session/history/{session_id}` - 获取历史
- `DELETE /api/session/{session_id}` - 清空会话

#### 学习记录
- `GET /api/records/{user_id}` - 获取记录
- `GET /api/records/statistics/{user_id}` - 获取统计
- `POST /api/records` - 添加记录

#### WebSocket
- `WS /ws/{user_id}` - 实时通信

### AI引擎 (port 8001)

- `POST /api/parse/multimodal` - 多模态解析
- `POST /api/reasoning/execute` - 执行推理
- `POST /api/knowledge/search` - 知识检索

## 技术栈

### 前端
- **框架**: Flutter
- **状态管理**: Provider
- **网络**: Dio, WebSocket
- **UI组件**: Material Design

### 后端
- **框架**: FastAPI
- **Web服务器**: Uvicorn
- **WebSocket**: python-websockets
- **异步处理**: asyncio

### AI引擎
- **多模态**: VLM (Vision Language Model)
- **LLM**: OpenAI / 文心一言 / 通义千问
- **知识检索**: 向量数据库 (Qdrant/Milvus)
- **OCR**: PaddleOCR
- **ASR**: Whisper

## 配置说明

### 后端配置 (.env)

```env
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000

# 数据库
DB_HOST=localhost
DB_PORT=5432
DB_NAME=numbersfall

# AI模型
OPENAI_API_KEY=your_key
WENXIN_API_KEY=your_key
```

### 移动端配置

修改 `lib/core/constants.dart`:
```dart
static const String apiBaseUrl = 'http://your-server:8000';
static const String wsBaseUrl = 'ws://your-server:8000';
```

## 开发路线图

- [x] 基础架构搭建
- [x] 多模态采集模块
- [x] 会话管理系统
- [x] 学习记录功能
- [ ] 集成真实LLM/VLM
- [ ] 向量数据库集成
- [ ] 用户认证系统
- [ ] 数据持久化
- [ ] 3D可视化渲染
- [ ] 离线模式支持

## 许可证

MIT License

## 联系方式

- 项目地址: [GitHub仓库]
- 问题反馈: [Issues]

---

**注意**: 本项目为框架代码，部分AI功能需要配置实际的API密钥和服务才能使用。
