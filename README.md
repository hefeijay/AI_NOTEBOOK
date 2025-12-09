# AI笔记应用

一个基于Vue 3和FastAPI的AI驱动笔记应用，支持实时协作编辑和AI智能润色。

## 技术栈

### 前端
- Vue 3 + TypeScript
- Vuex 4 (状态管理)
- Vue Router (路由)
- Vite (构建工具)
- WebSocket (实时通信)

### 后端
- FastAPI (Python)
- WebSocket (实时协作)
- SQLite/PostgreSQL (数据库)
- OpenAI API (AI服务)

## 项目结构

```
AINotebook/
├── frontend/          # Vue前端项目
│   ├── src/
│   │   ├── components/    # 组件
│   │   ├── views/         # 页面视图
│   │   ├── store/         # Vuex状态管理
│   │   ├── services/      # API服务
│   │   └── utils/         # 工具函数
│   └── package.json
├── backend/           # FastAPI后端项目
│   ├── app/
│   │   ├── main.py        # FastAPI入口
│   │   ├── models.py      # 数据模型
│   │   ├── routes/        # API路由
│   │   ├── services/      # 业务逻辑
│   │   └── websocket/     # WebSocket处理
│   └── requirements.txt
├── docker-compose.yml # 本地开发
└── README.md
```

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.11+
- OpenAI API Key

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd AINotebook
```

#### 2. 配置后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

编辑 `.env` 文件，设置 OpenAI API Key：

```
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///./notes.db
```

#### 3. 配置前端

```bash
cd frontend
npm install
cp .env.example .env
```

编辑 `.env` 文件：

```
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

#### 4. 启动服务

**启动后端：**

```bash
cd backend
uvicorn app.main:app --reload
```

后端将在 http://localhost:8000 启动

**启动前端：**

```bash
cd frontend
npm run dev
```

前端将在 http://localhost:3000 启动

## 功能特性

- ✅ **笔记管理**：创建、编辑、删除笔记
- ✅ **AI智能润色**：使用OpenAI API进行文本润色和扩展
- ✅ **流式响应**：AI响应以流式方式实时显示
- ✅ **文本选中处理**：支持选中部分文本进行AI处理
- ✅ **WebSocket实时协作**：多用户实时同步编辑
- ✅ **响应式设计**：支持桌面端和移动端
- ✅ **性能优化**：长文本流式渲染优化，避免卡顿

## 使用说明

### 创建笔记

1. 点击"新建笔记"按钮
2. 输入标题和内容
3. 内容会自动保存

### AI处理

1. 在笔记编辑页面，可以：
   - 选中部分文本，点击"AI处理"按钮（只处理选中部分）
   - 不选中任何文本，点击"AI处理"按钮（处理整篇笔记）
2. AI处理结果会以流式方式显示在悬浮框中
3. 点击"接受"应用AI处理结果，或点击"丢弃"取消

### 实时协作

- 打开多个浏览器标签页，同时编辑同一篇笔记
- 修改会自动同步到其他标签页

## API文档

后端启动后，访问 http://localhost:8000/docs 查看Swagger API文档。

## 部署

详细部署说明请参考 [DEPLOY.md](./DEPLOY.md)

### 快速部署到 Sealos

1. 构建Docker镜像
2. 在Sealos创建应用
3. 配置环境变量
4. 设置域名

## 开发

### 代码规范

- 使用 TypeScript，避免使用 `any`
- 使用 Vue 3 Composition API
- 遵循 ESLint 规则
- 组件样式使用 scoped CSS

### 测试

```bash
# 前端测试
cd frontend
npm run test

# 后端测试
cd backend
pytest
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
