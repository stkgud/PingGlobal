from flask import Flask, jsonify, request
import subprocess
import json
import os
import time
import threading
import socket
import ipaddress
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
# 配置CORS，允许来自前端域名的请求
CORS(app, resources={r"/api/*": {"origins": ["https://ping.nimangba.com", "http://localhost:4887"]}})

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
RESULTS_FILE = os.path.join(os.path.dirname(__file__), 'ping_results.json')

# 默认配置
default_config = {
    "servers": [
        {"id": "server1", "name": "美国服务器", "ipv4": "8.8.8.8", "ipv6": "2001:4860:4860::8888"},
        {"id": "server2", "name": "中国服务器", "ipv4": "114.114.114.114", "ipv6": None},
    ],
    "ping_interval": 300,  # 5分钟
    "ping_count": 5,
    "timeout": 5
}

# 全局变量
ping_results = {}
is_pinging = False
ping_thread = None

def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        # 如果配置文件不存在，创建默认配置
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config

def save_results():
    """保存ping结果到文件"""
    with open(RESULTS_FILE, 'w') as f:
        json.dump(ping_results, f, indent=2)

def is_ipv6_available():
    """检查系统是否支持IPv6"""
    try:
        socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        return True
    except:
        return False

def ping_server(source_ip, target_ip, count, timeout):
    """执行ping命令并返回结果"""
    try:
        # 判断IP类型
        is_ipv6 = False
        try:
            ip = ipaddress.ip_address(target_ip)
            is_ipv6 = ip.version == 6
        except ValueError:
            pass  # 不是有效IP，可能是域名
        
        # 构建ping命令
        if is_ipv6:
            cmd = ['ping6', '-c', str(count), '-W', str(timeout), target_ip]
        else:
            cmd = ['ping', '-c', str(count), '-W', str(timeout), target_ip]
        
        # 执行ping命令
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout*count+5)
        output = result.stdout
        
        # 解析ping结果
        if result.returncode == 0:
            # 提取平均延迟
            for line in output.splitlines():
                if 'avg' in line:
                    parts = line.split('=')[-1].strip().split('/')
                    if len(parts) >= 2:
                        avg_ms = float(parts[1])
                        return {
                            "status": "success",
                            "latency": avg_ms,
                            "raw_output": output
                        }
        
        return {
            "status": "failed",
            "latency": None,
            "raw_output": output
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "latency": None,
            "raw_output": "Ping command timed out"
        }
    except Exception as e:
        return {
            "status": "error",
            "latency": None,
            "raw_output": str(e)
        }

def ping_all_servers():
    """对所有服务器执行ping测试"""
    global ping_results, is_pinging
    
    config = load_config()
    servers = config["servers"]
    count = config["ping_count"]
    timeout = config["timeout"]
    
    while is_pinging:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results = {
            "timestamp": current_time,
            "data": {}
        }
        
        # 对每个源服务器
        for source in servers:
            source_id = source["id"]
            results["data"][source_id] = {}
            
            # 对每个目标服务器
            for target in servers:
                target_id = target["id"]
                if source_id == target_id:
                    # 跳过自己
                    results["data"][source_id][target_id] = {
                        "ipv4": {"status": "self", "latency": 0},
                        "ipv6": {"status": "self", "latency": 0}
                    }
                    continue
                
                results["data"][source_id][target_id] = {}
                
                # IPv4 ping
                if source.get("ipv4") and target.get("ipv4"):
                    results["data"][source_id][target_id]["ipv4"] = ping_server(
                        source["ipv4"], target["ipv4"], count, timeout
                    )
                else:
                    results["data"][source_id][target_id]["ipv4"] = {
                        "status": "unavailable",
                        "latency": None
                    }
                
                # IPv6 ping
                if source.get("ipv6") and target.get("ipv6") and is_ipv6_available():
                    results["data"][source_id][target_id]["ipv6"] = ping_server(
                        source["ipv6"], target["ipv6"], count, timeout
                    )
                else:
                    results["data"][source_id][target_id]["ipv6"] = {
                        "status": "unavailable",
                        "latency": None
                    }
        
        # 更新结果
        ping_results = results
        save_results()
        
        # 等待下一次ping
        time.sleep(config["ping_interval"])

def start_ping_thread():
    """启动ping线程"""
    global ping_thread, is_pinging
    
    if not is_pinging:
        is_pinging = True
        ping_thread = threading.Thread(target=ping_all_servers)
        ping_thread.daemon = True
        ping_thread.start()

def stop_ping_thread():
    """停止ping线程"""
    global is_pinging
    is_pinging = False

@app.route('/api/servers', methods=['GET'])
def get_servers():
    """获取所有服务器信息"""
    config = load_config()
    return jsonify(config["servers"])

@app.route('/api/servers', methods=['POST'])
def update_servers():
    """更新服务器配置"""
    config = load_config()
    new_servers = request.json
    
    if not isinstance(new_servers, list):
        return jsonify({"error": "Invalid server data"}), 400
    
    config["servers"] = new_servers
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    return jsonify({"status": "success"})

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    config = load_config()
    return jsonify(config)

@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置信息"""
    config = load_config()
    new_config = request.json
    
    for key, value in new_config.items():
        if key in config and key != "servers":
            config[key] = value
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    return jsonify({"status": "success"})

@app.route('/api/ping/results', methods=['GET'])
def get_ping_results():
    """获取ping结果"""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            return jsonify(json.load(f))
    else:
        return jsonify({"timestamp": "", "data": {}})

@app.route('/api/ping/start', methods=['POST'])
def start_ping():
    """启动ping测试"""
    start_ping_thread()
    return jsonify({"status": "started"})

@app.route('/api/ping/stop', methods=['POST'])
def stop_ping():
    """停止ping测试"""
    stop_ping_thread()
    return jsonify({"status": "stopped"})

@app.route('/api/ping/status', methods=['GET'])
def ping_status():
    """获取ping状态"""
    return jsonify({"is_running": is_pinging})

@app.route('/api/time', methods=['GET'])
def get_current_time():
    """获取当前时间"""
    current_time = subprocess.run(['date'], capture_output=True, text=True).stdout.strip()
    return jsonify({"time": current_time})

# 允许跨域请求
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

if __name__ == '__main__':
    # 启动时自动开始ping
    start_ping_thread()
    app.run(host='0.0.0.0', port=4888, debug=True) 