#!/bin/bash

echo "正在启动PingGlobal监控系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: 未检测到Docker。请先安装Docker和Docker Compose。"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "错误: 未检测到Docker Compose。请先安装Docker Compose。"
    exit 1
fi

# 启动服务
echo "正在启动Docker容器..."
docker-compose up -d

# 检查服务是否启动成功
if [ $? -eq 0 ]; then
    echo "PingGlobal监控系统已成功启动!"
    echo "请访问 http://localhost:4887 查看监控界面"
    echo "后端API运行在 http://localhost:4888"
else
    echo "启动失败，请检查错误信息。"
fi
