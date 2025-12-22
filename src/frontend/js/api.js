// API通信模块
var API = {
    // API基础URL
    baseURL: 'http://localhost:5000',
    
    // 获取本地存储的token
    getToken: function() {
        return localStorage.getItem('token');
    },
    
    // 设置本地存储的token
    setToken: function(token) {
        localStorage.setItem('token', token);
    },
    
    // 移除本地存储的token
    removeToken: function() {
        localStorage.removeItem('token');
    },
    
    // 通用请求函数
    request: function(endpoint, method, data) {
        method = method || 'GET';
        data = data || null;
        
        var headers = {
            'Content-Type': 'application/json'
        };
        
        // 如果有token，添加到请求头
        var token = this.getToken();
        if (token) {
            headers['Authorization'] = 'Bearer ' + token;
        }
        
        var config = {
            method: method,
            headers: headers
        };
        
        // 如果有数据，添加到请求体
        if (data) {
            config.body = JSON.stringify(data);
        }
        
        // 创建Promise对象处理异步请求
        return new Promise(function(resolve, reject) {
            fetch(API.baseURL + endpoint, config)
                .then(function(response) {
                    return response.json();
                })
                .then(function(result) {
                    // 检查响应格式，如果是标准格式，提取data字段
                    if (result && typeof result === 'object' && 'success' in result) {
                        if (result.success) {
                            resolve(result.data);
                        } else {
                            console.error('API请求失败:', result.message);
                            reject(new Error(result.message || 'API请求失败'));
                        }
                    } else {
                        // 非标准格式，直接返回
                        resolve(result);
                    }
                })
                .catch(function(error) {
                    console.error('API请求错误:', error);
                    reject(error);
                });
        });
    }
};

// 认证相关API
API.auth = {
    // 用户登录
    login: function(username, password) {
        return API.request('/api/auth/login', 'POST', { username: username, password: password });
    },
    
    // 用户注册
    register: function(username, password, email, fullName, phone) {
        return API.request('/api/auth/register', 'POST', { 
            username: username, 
            password: password, 
            email: email,
            full_name: fullName,
            phone: phone
        });
    },
    
    // 获取当前用户信息
    getCurrentUser: function() {
        return API.request('/api/auth/me');
    }
};

// 告警相关API
API.alarm = {
    // 获取所有告警
    getAllAlarms: function() {
        return API.request('/api/alarm');
    },
    
    // 获取未处理的告警
    getPendingAlarms: function() {
        return API.request('/api/alarm/pending');
    },
    
    // 处理告警
    handleAlarm: function(alarmId) {
        return API.request('/api/alarm/' + alarmId + '/handle', 'PUT');
    }
};

// 能源相关API
API.energy = {
    // 获取所有设备
    getAllDevices: function() {
        return API.request('/api/energy/devices');
    },
    
    // 获取能源监控数据
    getEnergyData: function() {
        return API.request('/api/energy/data');
    },
    
    // 获取能源趋势数据
    getEnergyTrend: function(startDate, endDate) {
        return API.request('/api/energy/trend?start=' + startDate + '&end=' + endDate);
    }
};

// 仪表板相关API
API.dashboard = {
    // 获取仪表板统计数据
    getSummaryData: function() {
        return API.request('/api/dashboard/summary');
    },
    
    // 获取实时数据
    getRealtimeData: function() {
        return API.request('/api/dashboard/realtime');
    }
};
