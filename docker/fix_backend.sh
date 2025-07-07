#!/bin/bash

echo "正在修复PingGlobal后端服务..."

# 停止后端容器
echo "停止后端容器..."
docker-compose stop backend

# 删除后端容器
echo "删除后端容器..."
docker-compose rm -f backend

# 删除后端镜像
echo "删除后端镜像..."
docker rmi ping_global_backend 2>/dev/null || true

# 强制重新构建后端镜像
echo "重新构建后端镜像..."
docker-compose build --no-cache backend

# 启动后端服务
echo "启动后端服务..."
docker-compose up -d backend

# 检查服务是否启动成功
if [ $? -eq 0 ]; then
    echo "等待5秒钟让服务启动..."
    sleep 5
    
    echo "PingGlobal后端服务已重建并启动!"
    echo "后端API运行在 http://localhost:4888"
    
    # 显示容器日志
    echo ""
    echo "后端容器日志："
    docker logs ping_global_backend
else
    echo "启动失败，请检查错误信息。"
fi

# 检查容器状态
echo ""
echo "容器状态："
docker-compose ps 