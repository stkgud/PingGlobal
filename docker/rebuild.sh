#!/bin/bash

echo "正在重新构建PingGlobal监控系统..."

# 停止并删除现有容器
echo "停止并删除现有容器..."
docker-compose down

# 删除旧的镜像
echo "删除旧的镜像..."
docker rmi ping_global_backend ping_global_frontend 2>/dev/null || true

# 重新构建镜像
echo "重新构建镜像..."
docker-compose build --no-cache

# 启动服务
echo "启动服务..."
docker-compose up -d

# 检查服务是否启动成功
if [ $? -eq 0 ]; then
    echo "PingGlobal监控系统已成功重建并启动!"
    echo "请访问 http://localhost:4887 查看监控界面"
    echo "后端API运行在 http://localhost:4888"
    
    # 显示容器日志
    echo ""
    echo "后端容器日志："
    docker logs ping_global_backend
else
    echo "启动失败，请检查错误信息。"
fi 