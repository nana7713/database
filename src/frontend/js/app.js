// 主应用逻辑
var App = {
    // 初始化应用
    init: function() {
        this.bindEvents();
        this.checkAuth();
    },
    
    // 绑定事件
    bindEvents: function() {
        // 登录按钮事件
        var loginBtn = document.getElementById('login-btn');
        if (loginBtn) {
            var self = this;
            loginBtn.addEventListener('click', function() { self.login(); });
        }
        
        // 注册链接事件
        var registerLink = document.getElementById('register-link');
        if (registerLink) {
            var self = this;
            registerLink.addEventListener('click', function(e) {
                e.preventDefault();
                self.showRegisterForm();
            });
        }
        
        // 注册按钮事件
        var registerBtn = document.getElementById('register-btn');
        if (registerBtn) {
            var self = this;
            registerBtn.addEventListener('click', function() { self.register(); });
        }
        
        // 返回登录链接事件
        var loginBackLink = document.getElementById('login-back-link');
        if (loginBackLink) {
            var self = this;
            loginBackLink.addEventListener('click', function(e) {
                e.preventDefault();
                self.showLoginForm();
            });
        }
        
        // 退出登录事件
        var logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            var self = this;
            logoutBtn.addEventListener('click', function() { self.logout(); });
        }
        
        // 菜单点击事件
        var menuItems = document.querySelectorAll('.menu-item');
        if (menuItems) {
            var self = this;
            menuItems.forEach(function(item) {
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    self.switchPage(item.dataset.page);
                });
            });
        }
        
        // 刷新告警按钮
        var refreshAlarmsBtn = document.getElementById('refresh-alarms');
        if (refreshAlarmsBtn) {
            var self = this;
            refreshAlarmsBtn.addEventListener('click', function() { self.loadAlarms(); });
        }
        
        // 刷新设备按钮
        var refreshDevicesBtn = document.getElementById('refresh-devices');
        if (refreshDevicesBtn) {
            var self = this;
            refreshDevicesBtn.addEventListener('click', function() { self.loadDevices(); });
        }
        
        // 回车键登录
        var usernameInput = document.getElementById('username');
        if (usernameInput) {
            var self = this;
            usernameInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    self.login();
                }
            });
        }
        
        var passwordInput = document.getElementById('password');
        if (passwordInput) {
            var self = this;
            passwordInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    self.login();
                }
            });
        }
    },
    
    // 检查用户认证状态
    async checkAuth() {
        var token = API.getToken();
        if (token) {
            try {
                var user = await API.auth.getCurrentUser();
                this.showMainApp(user);
            } catch (error) {
                // Token无效，清除并显示登录界面
                API.removeToken();
                this.showLoginForm();
            }
        } else {
            this.showLoginForm();
        }
    },
    
    // 显示登录表单
    showLoginForm() {
        var loginContainer = document.getElementById('login-container');
        if (loginContainer) {
            loginContainer.classList.remove('hidden');
            loginContainer.style.display = 'flex';
        }
        
        var loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.style.display = 'block';
        }
        
        var registerForm = document.getElementById('register-form');
        if (registerForm) {
            registerForm.style.display = 'none';
        }
        
        var mainContainer = document.getElementById('main-container');
        if (mainContainer) {
            mainContainer.style.display = 'none';
        }
    },
    
    // 显示注册表单
    showRegisterForm() {
        var loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.style.display = 'none';
        }
        
        var registerForm = document.getElementById('register-form');
        if (registerForm) {
            registerForm.style.display = 'block';
        }
    },
    
    // 用户注册
    async register() {
        var usernameInput = document.getElementById('reg-username');
        var emailInput = document.getElementById('reg-email');
        var passwordInput = document.getElementById('reg-password');
        var fullnameInput = document.getElementById('reg-fullname');
        var phoneInput = document.getElementById('reg-phone');
        
        var username = usernameInput ? usernameInput.value : '';
        var email = emailInput ? emailInput.value : '';
        var password = passwordInput ? passwordInput.value : '';
        var fullName = fullnameInput ? fullnameInput.value : '';
        var phone = phoneInput ? phoneInput.value : '';
        
        if (!username || !email || !password) {
            alert('用户名、邮箱和密码不能为空！');
            return;
        }
        
        try {
            var result = await API.auth.register(username, password, email, fullName, phone);
            alert('注册成功！请登录。');
            this.showLoginForm();
        } catch (error) {
            alert('注册失败：' + error.message);
        }
    },
    
    // 显示主应用界面
    showMainApp(user) {
        var loginContainer = document.getElementById('login-container');
        if (loginContainer) {
            loginContainer.style.display = 'none';
        }
        
        var mainContainer = document.getElementById('main-container');
        if (mainContainer) {
            mainContainer.style.display = 'flex';
        }
        
        // 更新当前用户信息
        var currentUser = document.getElementById('current-user');
        if (currentUser) {
            currentUser.textContent = '欢迎，' + user.username;
        }
        
        // 加载仪表板数据
        this.loadDashboardData();
        
        // 加载告警数据
        this.loadAlarms();
        
        // 加载设备数据
        this.loadDevices();
    },
    
    // 用户登录
    async login() {
        var usernameInput = document.getElementById('username');
        var passwordInput = document.getElementById('password');
        
        var username = usernameInput ? usernameInput.value : '';
        var password = passwordInput ? passwordInput.value : '';
        
        if (!username || !password) {
            alert('请输入用户名和密码！');
            return;
        }
        
        try {
            var result = await API.auth.login(username, password);
            
            if (result && result.token) {
                // 保存token
                API.setToken(result.token);
                
                // 显示主应用
                this.showMainApp(result.user);
            } else {
                alert('登录失败');
            }
        } catch (error) {
            alert('登录失败：' + error.message);
        }
    },
    
    // 用户登出
    logout() {
        API.removeToken();
        this.showLoginForm();
        
        // 清除输入框
        var usernameInput = document.getElementById('username');
        if (usernameInput) {
            usernameInput.value = '';
        }
        
        var passwordInput = document.getElementById('password');
        if (passwordInput) {
            passwordInput.value = '';
        }
    },
    
    // 切换页面
    switchPage(pageName) {
        // 更新菜单激活状态
        var menuItems = document.querySelectorAll('.menu-item');
        if (menuItems) {
            menuItems.forEach(function(item) {
                item.classList.remove('active');
            });
        }
        
        var targetMenuItem = document.querySelector('[data-page="' + pageName + '"]');
        if (targetMenuItem) {
            targetMenuItem.classList.add('active');
        }
        
        // 更新页面显示
        var pages = document.querySelectorAll('.page');
        if (pages) {
            pages.forEach(function(page) {
                page.classList.remove('active');
            });
        }
        
        var targetPage = document.getElementById(pageName + '-page');
        if (targetPage) {
            targetPage.classList.add('active');
        }
    },
    
    // 加载仪表板数据
    async loadDashboardData() {
        try {
            var data = await API.dashboard.getSummaryData();
            
            // 更新仪表板卡片数据
            var totalAlarms = document.getElementById('total-alarms');
            if (totalAlarms) {
                totalAlarms.textContent = data.totalAlarms || 0;
            }
            
            var pendingAlarms = document.getElementById('pending-alarms');
            if (pendingAlarms) {
                pendingAlarms.textContent = data.pendingAlarms || 0;
            }
            
            var totalEnergy = document.getElementById('total-energy');
            if (totalEnergy) {
                totalEnergy.textContent = (data.totalEnergy || 0).toFixed(2);
            }
            
            var peakLoad = document.getElementById('peak-load');
            if (peakLoad) {
                peakLoad.textContent = (data.peakLoad || 0).toFixed(2);
            }
        } catch (error) {
            console.error('加载仪表板数据失败:', error);
            // 使用模拟数据
            this.loadMockDashboardData();
        }
    },
    
    // 加载模拟仪表板数据
    loadMockDashboardData() {
        var totalAlarms = document.getElementById('total-alarms');
        if (totalAlarms) {
            totalAlarms.textContent = '15';
        }
        
        var pendingAlarms = document.getElementById('pending-alarms');
        if (pendingAlarms) {
            pendingAlarms.textContent = '5';
        }
        
        var totalEnergy = document.getElementById('total-energy');
        if (totalEnergy) {
            totalEnergy.textContent = '2450.80';
        }
        
        var peakLoad = document.getElementById('peak-load');
        if (peakLoad) {
            peakLoad.textContent = '125.50';
        }
    },
    
    // 加载告警数据
    loadAlarms: function() {
        var self = this;
        try {
            API.alarm.getAllAlarms().then(function(data) {
                self.renderAlarms(data);
            }).catch(function(error) {
                console.error('加载告警数据失败:', error);
                // 使用模拟数据
                self.loadMockAlarms();
            });
        } catch (error) {
            console.error('加载告警数据失败:', error);
            // 使用模拟数据
            self.loadMockAlarms();
        }
    },
    
    // 加载模拟告警数据
    loadMockAlarms: function() {
        var mockAlarms = [
            { alarm_id: 1, device_id: '1001', alarm_type: '温度异常', alarm_time: '2025-12-20 10:30:00', alarm_level: '高', alarm_content: '设备温度超过阈值', status: '未处理' },
            { alarm_id: 2, device_id: '1002', alarm_type: '电压异常', alarm_time: '2025-12-20 09:45:00', alarm_level: '中', alarm_content: '电压波动过大', status: '已处理' },
            { alarm_id: 3, device_id: '1003', alarm_type: '电流异常', alarm_time: '2025-12-20 08:15:00', alarm_level: '高', alarm_content: '电流超过额定值', status: '未处理' },
            { alarm_id: 4, device_id: '1004', alarm_type: '通信故障', alarm_time: '2025-12-19 16:30:00', alarm_level: '低', alarm_content: '设备通信中断', status: '已处理' },
            { alarm_id: 5, device_id: '1005', alarm_type: '功率异常', alarm_time: '2025-12-19 14:20:00', alarm_level: '中', alarm_content: '功率因数过低', status: '未处理' }
        ];
        this.renderAlarms(mockAlarms);
    },
    
    // 渲染告警列表
    renderAlarms: function(alarms) {
        var tbody = document.getElementById('alarm-table-body');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        var self = this;
        alarms.forEach(function(alarm) {
            var row = document.createElement('tr');
            row.innerHTML = 
                '<td>' + alarm.alarm_id + '</td>' +
                '<td>' + alarm.device_id + '</td>' +
                '<td>' + alarm.alarm_type + '</td>' +
                '<td>' + alarm.alarm_time + '</td>' +
                '<td><span class="alarm-level ' + alarm.alarm_level.toLowerCase() + '">' + alarm.alarm_level + '</span></td>' +
                '<td>' + alarm.alarm_content + '</td>' +
                '<td><span class="alarm-status ' + (alarm.status === '已处理' ? 'resolved' : 'pending') + '">' + alarm.status + '</span></td>' +
                '<td>' + (alarm.status === '未处理' ? '<button class="btn btn-sm btn-primary handle-alarm" data-alarm-id="' + alarm.alarm_id + '">处理</button>' : '') + '</td>';
            tbody.appendChild(row);
        });
        
        // 绑定处理告警按钮事件
        var handleButtons = document.querySelectorAll('.handle-alarm');
        if (handleButtons) {
            handleButtons.forEach(function(button) {
                button.addEventListener('click', function() {
                    var alarmId = this.getAttribute('data-alarm-id');
                    self.handleAlarm(alarmId);
                });
            });
        }
    },
    
    // 加载设备数据
    async loadDevices() {
        try {
            const data = await API.energy.getAllDevices();
            this.renderDevices(data);
        } catch (error) {
            console.error('加载设备数据失败:', error);
            // 使用模拟数据
            this.loadMockDevices();
        }
    },
    
    // 加载模拟设备数据
    loadMockDevices() {
        const mockDevices = [
            { device_id: '1001', device_name: '变压器A', device_type: '变压器', installation_location: '变电站1', status: '正常' },
            { device_id: '1002', device_name: '变压器B', device_type: '变压器', installation_location: '变电站2', status: '正常' },
            { device_id: '1003', device_name: '高压开关柜1', device_type: '开关柜', installation_location: '变电站1', status: '正常' },
            { device_id: '1004', device_name: '高压开关柜2', device_type: '开关柜', installation_location: '变电站2', status: '异常' },
            { device_id: '1005', device_name: '低压开关柜1', device_type: '开关柜', installation_location: '变电站1', status: '正常' },
            { device_id: '1006', device_name: '低压开关柜2', device_type: '开关柜', installation_location: '变电站2', status: '正常' }
        ];
        this.renderDevices(mockDevices);
    },
    
    // 渲染设备列表
    renderDevices(devices) {
        const tbody = document.getElementById('device-table-body');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        devices.forEach(device => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${device.device_id}</td>
                <td>${device.device_name}</td>
                <td>${device.device_type}</td>
                <td>${device.installation_location}</td>
                <td><span class="device-status ${device.status === '正常' ? 'normal' : 'abnormal'}">${device.status}</span></td>
            `;
            tbody.appendChild(row);
        });
    }
};

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
