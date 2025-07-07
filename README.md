# PingGlobal - 全球服务器Ping监控系统

PingGlobal是一个用于监控全球服务器之间网络延迟的系统。它支持IPv4和IPv6，并提供友好的Web界面来展示服务器之间的ping值。

## 功能特点

- 支持监控多台全球分布的服务器
- 同时支持IPv4和IPv6网络
- 实时显示服务器之间的ping延迟
- 直观的矩阵视图展示所有服务器之间的连接状态
- 可自定义ping参数（间隔、次数、超时时间）
- 服务器管理界面，可以添加、删除和编辑服务器
- 使用Docker容器化部署，便于安装和维护

## 系统要求

- Docker和Docker Compose
- 互联网连接

## 快速开始

### 使用Docker Compose启动

1. 克隆本仓库：

```bash
git clone https://github.com/yourusername/PingGlobal.git
cd PingGlobal
```

2. 启动服务：

```bash
docker-compose up -d
```

3. 访问Web界面：

打开浏览器，访问 `http://localhost`

### 手动启动（开发模式）

1. 启动后端：

```bash
cd backend
pip install -r requirements.txt
python app.py
```

2. 启动前端：

可以使用任何HTTP服务器提供前端文件，例如：

```bash
cd frontend
python -m http.server 8080
```

然后访问 `http://localhost:8080`

注意：后端API将在 `http://localhost:4888` 上运行

## 配置服务器

1. 在Web界面中，点击"服务器管理"标签
2. 添加、编辑或删除服务器
3. 每台服务器需要提供以下信息：
   - ID：服务器唯一标识符
   - 名称：显示名称
   - IPv4地址（可选）
   - IPv6地址（可选）

## 系统架构

- 后端：使用Flask构建的RESTful API
- 前端：基于Vue.js和Bootstrap的响应式Web界面
- 容器化：使用Docker和Docker Compose进行部署

## 注意事项

- 服务器需要允许ICMP流量才能正确响应ping请求
- 某些云服务提供商可能会限制或禁止ICMP流量
- IPv6功能需要系统和网络支持IPv6

## 许可证

MIT
