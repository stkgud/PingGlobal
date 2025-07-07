# Cloudflare Tunnel 配置指南

## 前提条件

1. 已注册Cloudflare账户
2. 已将域名 `nimangba.com` 添加到Cloudflare并完成DNS设置
3. 已安装Cloudflare CLI工具 `cloudflared`

## 配置步骤

### 1. 登录Cloudflare

```bash
cloudflared tunnel login
```

这将打开浏览器，要求您授权CLI访问您的Cloudflare账户。

### 2. 创建隧道

```bash
cloudflared tunnel create pingglobal
```

这将创建一个名为"pingglobal"的隧道，并生成凭证文件。

### 3. 创建配置文件

创建 `~/.cloudflared/config.yml` 文件，内容如下：

```yaml
tunnel: <YOUR_TUNNEL_ID>
credentials-file: /path/to/credentials/file.json

ingress:
  # 前端服务
  - hostname: ping.nimangba.com
    service: http://localhost:4887
  
  # 后端API服务
  - hostname: api-ping.nimangba.com
    service: http://localhost:4888
  
  # 捕获所有其他请求
  - service: http_status:404
```

请将 `<YOUR_TUNNEL_ID>` 替换为您创建隧道时获得的ID，并更新凭证文件的路径。

### 4. 添加DNS记录

```bash
cloudflared tunnel route dns pingglobal ping.nimangba.com
cloudflared tunnel route dns pingglobal api-ping.nimangba.com
```

这将创建必要的DNS记录，将域名指向您的隧道。

### 5. 启动隧道

```bash
cloudflared tunnel run pingglobal
```

或者，您可以将其设置为系统服务：

```bash
cloudflared service install
```

### 6. 验证配置

现在您应该可以通过以下URL访问服务：

- 前端界面: https://ping.nimangba.com
- 后端API: https://api-ping.nimangba.com

## 故障排除

1. 检查隧道状态：
   ```bash
   cloudflared tunnel info pingglobal
   ```

2. 查看隧道日志：
   ```bash
   cloudflared tunnel info pingglobal --debug-level debug
   ```

3. 确保本地服务正在运行：
   ```bash
   docker-compose ps
   ```

4. 检查Cloudflare DNS记录是否正确配置：
   在Cloudflare仪表板中查看DNS记录 