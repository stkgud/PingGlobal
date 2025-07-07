// 全局API基础URL
const API_BASE_URL = 'http://localhost:4888/api';

// Vue应用
const app = Vue.createApp({
    data() {
        return {
            activeTab: 'dashboard',
            servers: [],
            editableServers: [],
            pingResults: null,
            pingStatus: false,
            config: {
                ping_interval: 300,
                ping_count: 5,
                timeout: 5
            },
            loading: false,
            error: null,
            currentTime: '',
            showIPv6: false,
            refreshInterval: null
        };
    },
    
    mounted() {
        // 初始化加载数据
        this.fetchServers();
        this.fetchConfig();
        this.fetchPingStatus();
        this.fetchPingResults();
        this.updateCurrentTime();
        
        // 设置定时刷新
        this.refreshInterval = setInterval(() => {
            this.fetchPingResults();
            this.fetchPingStatus();
            this.updateCurrentTime();
        }, 10000); // 每10秒刷新一次
    },
    
    beforeUnmount() {
        // 清除定时器
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    },
    
    methods: {
        // 获取当前时间
        updateCurrentTime() {
            this.loading = true;
            axios.get(`${API_BASE_URL}/time`)
                .then(response => {
                    this.currentTime = response.data.time;
                })
                .catch(error => {
                    console.error('获取时间失败:', error);
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        
        // 获取服务器列表
        fetchServers() {
            this.loading = true;
            axios.get(`${API_BASE_URL}/servers`)
                .then(response => {
                    this.servers = response.data;
                    this.editableServers = JSON.parse(JSON.stringify(this.servers));
                })
                .catch(error => {
                    this.error = '无法加载服务器列表: ' + error.message;
                    console.error('获取服务器列表失败:', error);
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        
        // 获取配置信息
        fetchConfig() {
            this.loading = true;
            axios.get(`${API_BASE_URL}/config`)
                .then(response => {
                    this.config = response.data;
                })
                .catch(error => {
                    this.error = '无法加载配置: ' + error.message;
                    console.error('获取配置失败:', error);
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        
        // 获取ping状态
        fetchPingStatus() {
            axios.get(`${API_BASE_URL}/ping/status`)
                .then(response => {
                    this.pingStatus = response.data.is_running;
                })
                .catch(error => {
                    console.error('获取ping状态失败:', error);
                });
        },
        
        // 获取ping结果
        fetchPingResults() {
            axios.get(`${API_BASE_URL}/ping/results`)
                .then(response => {
                    this.pingResults = response.data;
                })
                .catch(error => {
                    console.error('获取ping结果失败:', error);
                });
        },
        
        // 启动ping监控
        startPing() {
            this.loading = true;
            axios.post(`${API_BASE_URL}/ping/start`)
                .then(response => {
                    this.pingStatus = true;
                    this.error = null;
                })
                .catch(error => {
                    this.error = '启动监控失败: ' + error.message;
                    console.error('启动ping监控失败:', error);
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        
        // 停止ping监控
        stopPing() {
            this.loading = true;
            axios.post(`${API_BASE_URL}/ping/stop`)
                .then(response => {
                    this.pingStatus = false;
                    this.error = null;
                })
                .catch(error => {
                    this.error = '停止监控失败: ' + error.message;
                    console.error('停止ping监控失败:', error);
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        
        // 保存配置
        saveSettings() {
            this.loading = true;
            axios.post(`${API_BASE_URL}/config`, this.config)
                .then(response => {
                    this.error = null;
                    alert('设置已保存');
                })
                .catch(error => {
                    this.error = '保存设置失败: ' + error.message;
                    console.error('保存配置失败:', error);
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        
        // 添加新服务器
        addNewServer() {
            this.editableServers.push({
                id: `server${this.editableServers.length + 1}`,
                name: `服务器${this.editableServers.length + 1}`,
                ipv4: '',
                ipv6: '',
                isNew: true
            });
        },
        
        // 移除服务器
        removeServer(index) {
            this.editableServers.splice(index, 1);
        },
        
        // 保存服务器配置
        saveServers() {
            this.loading = true;
            
            // 移除临时属性
            const serversToSave = this.editableServers.map(server => {
                const { isNew, ...cleanServer } = server;
                return cleanServer;
            });
            
            axios.post(`${API_BASE_URL}/servers`, serversToSave)
                .then(response => {
                    this.error = null;
                    alert('服务器配置已保存');
                    this.fetchServers();
                })
                .catch(error => {
                    this.error = '保存服务器配置失败: ' + error.message;
                    console.error('保存服务器配置失败:', error);
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        
        // 获取单个服务器的平均延迟
        getAverageLatency(serverId) {
            const result = { ipv4: null, ipv6: null };
            
            if (!this.pingResults || !this.pingResults.data) {
                return result;
            }
            
            let ipv4Sum = 0;
            let ipv4Count = 0;
            let ipv6Sum = 0;
            let ipv6Count = 0;
            
            // 遍历所有其他服务器到该服务器的ping结果
            this.servers.forEach(source => {
                if (source.id === serverId) return;
                
                const sourceData = this.pingResults.data[source.id];
                if (!sourceData || !sourceData[serverId]) return;
                
                // IPv4
                if (sourceData[serverId].ipv4 && sourceData[serverId].ipv4.status === 'success') {
                    ipv4Sum += sourceData[serverId].ipv4.latency;
                    ipv4Count++;
                }
                
                // IPv6
                if (sourceData[serverId].ipv6 && sourceData[serverId].ipv6.status === 'success') {
                    ipv6Sum += sourceData[serverId].ipv6.latency;
                    ipv6Count++;
                }
            });
            
            if (ipv4Count > 0) {
                result.ipv4 = ipv4Sum / ipv4Count;
            }
            
            if (ipv6Count > 0) {
                result.ipv6 = ipv6Sum / ipv6Count;
            }
            
            return result;
        },
        
        // 获取矩阵单元格的CSS类
        getCellClass(sourceId, targetId) {
            if (sourceId === targetId) {
                return 'cell-self';
            }
            
            if (!this.pingResults || !this.pingResults.data || 
                !this.pingResults.data[sourceId] || 
                !this.pingResults.data[sourceId][targetId]) {
                return '';
            }
            
            const ipType = this.showIPv6 ? 'ipv6' : 'ipv4';
            const pingData = this.pingResults.data[sourceId][targetId][ipType];
            
            if (!pingData || pingData.status !== 'success') {
                return 'cell-danger';
            }
            
            const latency = pingData.latency;
            if (latency < 100) {
                return 'cell-success';
            } else if (latency < 300) {
                return 'cell-warning';
            } else {
                return 'cell-danger';
            }
        }
    }
});

// 挂载Vue应用
app.mount('#app');
