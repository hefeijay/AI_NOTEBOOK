# 部署指南

## Sealos 部署步骤

### 1. 准备工作

1. 注册并登录 [Sealos](https://cloud.sealos.io/)
2. 准备 OpenAI API Key

### 2. 后端部署

#### 2.1 构建 Docker 镜像

```bash
cd backend
docker build -t your-registry/ai-notebook-backend:latest .
docker push your-registry/ai-notebook-backend:latest
```

#### 2.2 在 Sealos 创建应用

1. 进入 Sealos 控制台
2. 选择"应用管理" -> "新建应用"
3. 配置如下：

**基本信息：**
- 应用名称：ai-notebook-backend
- 镜像：your-registry/ai-notebook-backend:latest
- 端口：8000

**环境变量：**
```
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///./notes.db
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

**存储：**
- 挂载路径：/app/data（用于SQLite数据库持久化）

### 3. 前端部署

#### 3.1 构建前端

```bash
cd frontend
npm install
npm run build
```

#### 3.2 部署静态文件

**方式一：使用 Sealos 静态托管**

1. 在 Sealos 控制台选择"静态网站托管"
2. 上传 `frontend/dist` 目录内容
3. 配置自定义域名（可选）

**方式二：使用 Nginx 容器**

1. 构建并推送前端 Docker 镜像
2. 在 Sealos 创建应用，使用前端镜像
3. 配置环境变量：
```
VITE_API_BASE_URL=https://your-backend-domain.com
VITE_WS_URL=wss://your-backend-domain.com/ws
```

### 4. 配置说明

#### 后端环境变量

- `OPENAI_API_KEY`: OpenAI API密钥（必需）
- `SECRET_KEY`: 应用密钥（用于JWT等，生产环境请使用强随机字符串）
- `DATABASE_URL`: 数据库连接字符串
  - SQLite: `sqlite:///./notes.db`
  - PostgreSQL: `postgresql://user:password@host:port/dbname`
- `CORS_ORIGINS`: 允许的跨域来源（JSON数组格式）

#### 前端环境变量

在构建时设置（通过 `.env` 文件或构建参数）：

- `VITE_API_BASE_URL`: 后端API地址
- `VITE_WS_URL`: WebSocket地址

### 5. 域名配置

1. 在 Sealos 为后端应用配置域名（如：api.yourdomain.com）
2. 在 Sealos 为前端应用配置域名（如：app.yourdomain.com）
3. 更新前端环境变量中的API地址

### 6. 数据库迁移（如使用PostgreSQL）

如果需要使用 PostgreSQL：

1. 在 Sealos 创建 PostgreSQL 数据库实例
2. 获取连接字符串
3. 更新后端环境变量 `DATABASE_URL`
4. 重启后端应用

### 7. 验证部署

1. 访问前端地址，应该能看到笔记列表页面
2. 创建一篇笔记，测试基本功能
3. 测试 AI 处理功能（需要配置 OpenAI API Key）
4. 测试 WebSocket 实时协作（打开多个标签页同时编辑）

## 本地开发

### 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

## 故障排查

### 常见问题

1. **CORS 错误**
   - 检查后端 `CORS_ORIGINS` 配置是否包含前端域名

2. **WebSocket 连接失败**
   - 检查 WebSocket URL 是否正确（ws:// 或 wss://）
   - 检查防火墙和负载均衡器配置

3. **AI 处理失败**
   - 检查 OpenAI API Key 是否正确
   - 检查 API 额度是否充足

4. **数据库连接失败**
   - 检查数据库连接字符串格式
   - 检查网络连接和权限

