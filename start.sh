#!/bin/bash

# AI笔记应用启动脚本

echo "🚀 启动AI笔记应用..."

# 检查后端环境变量
if [ ! -f "backend/.env" ]; then
    echo "⚠️  后端 .env 文件不存在，正在创建..."
    cp backend/.env.example backend/.env
    echo "📝 请编辑 backend/.env 文件，设置 OPENAI_API_KEY"
    read -p "按回车键继续..."
fi

# 检查前端环境变量
if [ ! -f "frontend/.env" ]; then
    echo "⚠️  前端 .env 文件不存在，正在创建..."
    cp frontend/.env.example frontend/.env
fi

# 启动后端
echo "🔧 启动后端服务..."
cd backend
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo "✅ 后端服务启动在 http://localhost:8000"
uvicorn app.main:app --reload &
BACKEND_PID=$!

cd ..

# 等待后端启动
sleep 3

# 启动前端
echo "🎨 启动前端服务..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

echo "✅ 前端服务启动在 http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✨ 应用已启动！"
echo "📝 前端: http://localhost:3000"
echo "🔧 后端: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

