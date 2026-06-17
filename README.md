# 语音待办 Todo App

一个语音驱动的待办事项应用，通过聊天界面使用文本或语音输入创建待办。

## 项目介绍

本项目是一个移动端待办事项管理应用，支持：
- 语音输入创建待办事项
- 聊天式智能待办解析
- 用户登录注册
- 待办分类管理（今天/周期/历史）
- 待办状态切换

## 技术栈

- **前端**：uni-app (Vue 3) + Vite
- **后端**：Python + FastAPI + MySQL
- **语音识别**：faster-whisper

## 运行项目

### 后端启动

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境并安装依赖：
```bash
uv venv
uv pip install -r requirements.txt
```

3. 配置 `backend/.env`：
```env
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=todo_app

# JWT 密钥
JWT_SECRET_KEY=your-secret-key

# 文件上传目录
UPLOAD_DIR=uploads
```

4. 启动服务：
```bash
uvicorn src.main:app --reload
```

后端运行在 `http://localhost:8000`，API 文档地址：`http://localhost:8000/docs`

### 前端启动

1. 进入前端目录：
```bash
cd frontend
```

2. 使用 HBuilderX 打开 `frontend` 目录，点击「运行」→「运行到手机或模拟器」→「运行到 Android App 基座」

## 目录说明

```text
to-do/
├── frontend/     # uni-app 前端
├── backend/      # FastAPI 后端
└── docs/         # 项目文档
```
