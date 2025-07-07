f#!/bin/bash

echo "正在修复PingGlobal前端服务..."

# 停止前端容器
echo "停止前端容器..."
docker-compose stop frontend

# 删除前端容器
echo "删除前端容器..."
docker-compose rm -f frontend

# 删除前端镜像
echo "删除前端镜像..."
docker rmi pingglobal-frontend 2>/dev/null || true

# 强制重新构建前端镜像
echo "重新构建前端镜像..."
docker-compose build --no-cache frontend

# 启动前端服务
echo "启动前端服务..."
docker-compose up -d frontend

# 检查服务是否启动成功
if [ $? -eq 0 ]; then
    echo "等待5秒钟让服务启动..."
    sleep 5
    
    echo "PingGlobal前端服务已重建并启动!"
    echo "前端界面运行在 http://localhost:4887"
    
    # 显示容器日志
    echo ""
    echo "前端容器日志："
    docker logs ping_global_frontend
else
    echo "启动失败，请检查错误信息。"
fi

# 检查容器状态
echo ""
echo "容器状态："
docker-compose ps 