/**
 * 🔧 管理後台 - JavaScript 檔案
 * 使用 jQuery 和 Bootstrap 5
 */

class AdminPanel {
    constructor() {
        this.apiBase = 'http://localhost:5000/api';
        this.token = localStorage.getItem('admin_token');
        this.currentUser = null;
        this.charts = {};
        
        this.init();
    }

    /**
     * 初始化管理後台
     */
    init() {
        this.setupEventListeners();
        this.checkAuthStatus();
        this.loadDashboard();
    }

    /**
     * 設定事件監聽器
     */
    setupEventListeners() {
        // 表單提交事件
        $('#addQuestionForm').on('submit', (e) => {
            e.preventDefault();
            this.addQuestion();
        });
        
        // 模態框關閉事件
        $('.modal').on('hidden.bs.modal', () => {
            this.clearForms();
        });
    }

    /**
     * 檢查認證狀態
     */
    checkAuthStatus() {
        if (this.token) {
            this.getCurrentUser();
        } else {
            this.showLoginPrompt();
        }
    }

    /**
     * 顯示登入提示
     */
    showLoginPrompt() {
        const loginHtml = `
            <div class="text-center py-5">
                <div class="game-card">
                    <div class="card-body">
                        <i class="fas fa-lock fa-3x text-warning mb-3"></i>
                        <h3>需要管理員權限</h3>
                        <p class="text-muted">請使用管理員帳號登入</p>
                        <button class="btn btn-primary" onclick="admin.showLoginModal()">
                            <i class="fas fa-sign-in-alt me-2"></i>登入
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        $('.container-fluid').html(loginHtml);
    }

    /**
     * API 請求函式
     */
    async apiRequest(endpoint, options = {}) {
        const url = `${this.apiBase}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        if (this.token) {
            config.headers.Authorization = `Bearer ${this.token}`;
        }
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || '請求失敗');
            }
            
            return data;
        } catch (error) {
            console.error('API 請求失敗:', error);
            this.showNotification(error.message, 'error');
            throw error;
        }
    }

    /**
     * 顯示通知
     */
    showNotification(message, type = 'info') {
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';
        
        const notification = $(`
            <div class="notification alert ${alertClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        $('body').append(notification);
        
        // 自動移除通知
        setTimeout(() => {
            notification.fadeOut(() => notification.remove());
        }, 5000);
    }

    /**
     * 取得當前使用者資訊
     */
    async getCurrentUser() {
        try {
            const data = await this.apiRequest('/auth/me');
            this.currentUser = data.user;
            this.updateAdminInfo();
        } catch (error) {
            console.error('取得使用者資訊失敗:', error);
            this.logout();
        }
    }

    /**
     * 更新管理員資訊顯示
     */
    updateAdminInfo() {
        if (this.currentUser) {
            $('#adminInfo').html(`
                <span class="navbar-text">
                    <i class="fas fa-user-shield"></i> ${this.currentUser.username}
                </span>
            `);
        }
    }

    /**
     * 登出
     */
    logout() {
        this.token = null;
        this.currentUser = null;
        localStorage.removeItem('admin_token');
        this.showLoginPrompt();
        this.showNotification('已登出', 'info');
    }

    /**
     * 顯示儀表板
     */
    showDashboard() {
        this.hideAllSections();
        $('#dashboardSection').show();
        this.updateActiveNav('dashboard');
        this.loadDashboard();
    }

    /**
     * 顯示題目管理
     */
    showQuestions() {
        this.hideAllSections();
        $('#questionsSection').show();
        this.updateActiveNav('questions');
        this.loadQuestions();
    }

    /**
     * 顯示使用者管理
     */
    showUsers() {
        this.hideAllSections();
        $('#usersSection').show();
        this.updateActiveNav('users');
        this.loadUsers();
    }

    /**
     * 顯示房間管理
     */
    showRooms() {
        this.hideAllSections();
        $('#roomsSection').show();
        this.updateActiveNav('rooms');
        this.loadRooms();
    }

    /**
     * 顯示統計資料
     */
    showStats() {
        this.hideAllSections();
        $('#statsSection').show();
        this.updateActiveNav('stats');
        this.loadStats();
    }

    /**
     * 隱藏所有區塊
     */
    hideAllSections() {
        $('#dashboardSection, #questionsSection, #usersSection, #roomsSection, #statsSection').hide();
    }

    /**
     * 更新導航狀態
     */
    updateActiveNav(section) {
        $('.nav-link').removeClass('active');
        $(`.nav-link[onclick*="${section}"]`).addClass('active');
    }

    /**
     * 載入儀表板資料
     */
    async loadDashboard() {
        try {
            // 載入統計資料
            const stats = await this.apiRequest('/admin/stats');
            this.updateDashboardStats(stats);
            
            // 載入最近活動
            const activities = await this.apiRequest('/admin/recent-activities');
            this.updateRecentActivities(activities);
            
            // 載入系統狀態
            const systemStatus = await this.apiRequest('/admin/system-status');
            this.updateSystemStatus(systemStatus);
            
        } catch (error) {
            console.error('載入儀表板失敗:', error);
        }
    }

    /**
     * 更新儀表板統計
     */
    updateDashboardStats(stats) {
        $('#totalUsers').text(stats.total_users || 0);
        $('#totalQuestions').text(stats.total_questions || 0);
        $('#activeRooms').text(stats.active_rooms || 0);
        $('#totalGames').text(stats.total_games || 0);
    }

    /**
     * 更新最近活動
     */
    updateRecentActivities(activities) {
        const activitiesHtml = activities.activities?.map(activity => `
            <div class="d-flex align-items-center mb-2">
                <div class="flex-shrink-0">
                    <i class="fas fa-circle text-primary"></i>
                </div>
                <div class="flex-grow-1 ms-3">
                    <div class="fw-bold">${activity.title}</div>
                    <small class="text-muted">${activity.time}</small>
                </div>
            </div>
        `).join('') || '<p class="text-muted">暫無活動</p>';
        
        $('#recentActivity').html(activitiesHtml);
    }

    /**
     * 更新系統狀態
     */
    updateSystemStatus(status) {
        const statusHtml = `
            <div class="row">
                <div class="col-6">
                    <div class="d-flex align-items-center mb-2">
                        <i class="fas fa-server text-success me-2"></i>
                        <span>資料庫連線</span>
                        <span class="badge bg-success ms-auto">正常</span>
                    </div>
                    <div class="d-flex align-items-center mb-2">
                        <i class="fas fa-memory text-success me-2"></i>
                        <span>記憶體使用</span>
                        <span class="badge bg-success ms-auto">${status.memory_usage || '正常'}</span>
                    </div>
                </div>
                <div class="col-6">
                    <div class="d-flex align-items-center mb-2">
                        <i class="fas fa-hdd text-success me-2"></i>
                        <span>磁碟空間</span>
                        <span class="badge bg-success ms-auto">${status.disk_usage || '正常'}</span>
                    </div>
                    <div class="d-flex align-items-center mb-2">
                        <i class="fas fa-network-wired text-success me-2"></i>
                        <span>網路連線</span>
                        <span class="badge bg-success ms-auto">正常</span>
                    </div>
                </div>
            </div>
        `;
        
        $('#systemStatus').html(statusHtml);
    }

    /**
     * 載入題目列表
     */
    async loadQuestions() {
        try {
            const data = await this.apiRequest('/questions?limit=100');
            this.displayQuestions(data.questions);
        } catch (error) {
            console.error('載入題目失敗:', error);
        }
    }

    /**
     * 顯示題目列表
     */
    displayQuestions(questions) {
        const questionsHtml = questions.map(question => `
            <tr>
                <td>${question.id}</td>
                <td>${question.question_text.substring(0, 50)}...</td>
                <td>${question.category}</td>
                <td>
                    <span class="badge bg-${this.getDifficultyColor(question.difficulty)}">
                        ${this.getDifficultyText(question.difficulty)}
                    </span>
                </td>
                <td>
                    <span class="badge bg-info">
                        ${this.getTypeText(question.question_type)}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="admin.editQuestion('${question.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="admin.deleteQuestion('${question.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        
        $('#questionsTable').html(questionsHtml);
    }

    /**
     * 取得難度顏色
     */
    getDifficultyColor(difficulty) {
        const colors = {
            'easy': 'success',
            'medium': 'warning',
            'hard': 'danger'
        };
        return colors[difficulty] || 'secondary';
    }

    /**
     * 取得難度文字
     */
    getDifficultyText(difficulty) {
        const texts = {
            'easy': '簡單',
            'medium': '中等',
            'hard': '困難'
        };
        return texts[difficulty] || difficulty;
    }

    /**
     * 取得題型文字
     */
    getTypeText(type) {
        const texts = {
            'multiple_choice': '選擇題',
            'multi_blank': '多重填空'
        };
        return texts[type] || type;
    }

    /**
     * 顯示新增題目模態框
     */
    showAddQuestionModal() {
        this.loadCategories();
        $('#addQuestionModal').modal('show');
    }

    /**
     * 載入分類
     */
    async loadCategories() {
        try {
            const data = await this.apiRequest('/questions/categories');
            const options = data.categories.map(category => 
                `<option value="${category}">${category}</option>`
            ).join('');
            
            $('#questionCategory').html('<option value="">選擇分類</option>' + options);
        } catch (error) {
            console.error('載入分類失敗:', error);
        }
    }

    /**
     * 新增題目
     */
    async addQuestion() {
        const formData = {
            question_text: $('#questionText').val(),
            category: $('#questionCategory').val(),
            difficulty: $('#questionDifficulty').val(),
            question_type: $('#questionType').val(),
            options: $('#questionOptions').val().split(',').map(opt => opt.trim()),
            answer: $('#questionAnswer').val(),
            explanation: $('#questionExplanation').val()
        };
        
        try {
            await this.apiRequest('/questions', {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            
            this.showNotification('題目新增成功！', 'success');
            $('#addQuestionModal').modal('hide');
            this.loadQuestions();
            
        } catch (error) {
            console.error('新增題目失敗:', error);
        }
    }

    /**
     * 編輯題目
     */
    editQuestion(questionId) {
        // 實作編輯題目功能
        this.showNotification('編輯功能開發中...', 'info');
    }

    /**
     * 刪除題目
     */
    async deleteQuestion(questionId) {
        if (!confirm('確定要刪除此題目嗎？')) return;
        
        try {
            await this.apiRequest(`/questions/${questionId}`, {
                method: 'DELETE'
            });
            
            this.showNotification('題目刪除成功！', 'success');
            this.loadQuestions();
            
        } catch (error) {
            console.error('刪除題目失敗:', error);
        }
    }

    /**
     * 載入使用者列表
     */
    async loadUsers() {
        try {
            const data = await this.apiRequest('/admin/users');
            this.displayUsers(data.users);
        } catch (error) {
            console.error('載入使用者失敗:', error);
        }
    }

    /**
     * 顯示使用者列表
     */
    displayUsers(users) {
        const usersHtml = users.map(user => `
            <tr>
                <td>${user.id}</td>
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td>${new Date(user.created_at).toLocaleString()}</td>
                <td>
                    <span class="badge bg-success">活躍</span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-warning me-1" onclick="admin.editUser('${user.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="admin.deleteUser('${user.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        
        $('#usersTable').html(usersHtml);
    }

    /**
     * 編輯使用者
     */
    editUser(userId) {
        this.showNotification('編輯功能開發中...', 'info');
    }

    /**
     * 刪除使用者
     */
    async deleteUser(userId) {
        if (!confirm('確定要刪除此使用者嗎？')) return;
        
        try {
            await this.apiRequest(`/admin/users/${userId}`, {
                method: 'DELETE'
            });
            
            this.showNotification('使用者刪除成功！', 'success');
            this.loadUsers();
            
        } catch (error) {
            console.error('刪除使用者失敗:', error);
        }
    }

    /**
     * 載入房間列表
     */
    async loadRooms() {
        try {
            const data = await this.apiRequest('/rooms');
            this.displayRooms(data.rooms);
        } catch (error) {
            console.error('載入房間失敗:', error);
        }
    }

    /**
     * 顯示房間列表
     */
    displayRooms(rooms) {
        const roomsHtml = rooms.map(room => `
            <tr>
                <td>${room.id}</td>
                <td>${room.name}</td>
                <td>${room.created_by_username || '未知'}</td>
                <td>${room.current_players}/${room.max_players}</td>
                <td>
                    <span class="badge bg-${this.getRoomStatusColor(room.status)}">
                        ${this.getRoomStatusText(room.status)}
                    </span>
                </td>
                <td>${new Date(room.created_at).toLocaleString()}</td>
                <td>
                    <button class="btn btn-sm btn-outline-danger" onclick="admin.deleteRoom('${room.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        
        $('#roomsTable').html(roomsHtml);
    }

    /**
     * 取得房間狀態顏色
     */
    getRoomStatusColor(status) {
        const colors = {
            'waiting': 'warning',
            'in_progress': 'success',
            'finished': 'secondary'
        };
        return colors[status] || 'secondary';
    }

    /**
     * 取得房間狀態文字
     */
    getRoomStatusText(status) {
        const texts = {
            'waiting': '等待中',
            'in_progress': '進行中',
            'finished': '已結束'
        };
        return texts[status] || status;
    }

    /**
     * 刪除房間
     */
    async deleteRoom(roomId) {
        if (!confirm('確定要刪除此房間嗎？')) return;
        
        try {
            await this.apiRequest(`/admin/rooms/${roomId}`, {
                method: 'DELETE'
            });
            
            this.showNotification('房間刪除成功！', 'success');
            this.loadRooms();
            
        } catch (error) {
            console.error('刪除房間失敗:', error);
        }
    }

    /**
     * 載入統計資料
     */
    async loadStats() {
        try {
            const stats = await this.apiRequest('/admin/stats');
            this.createCharts(stats);
        } catch (error) {
            console.error('載入統計資料失敗:', error);
        }
    }

    /**
     * 建立圖表
     */
    createCharts(stats) {
        // 題目分類統計圖
        const categoryCtx = document.getElementById('categoryChart');
        if (categoryCtx) {
            this.charts.category = new Chart(categoryCtx, {
                type: 'pie',
                data: {
                    labels: stats.category_stats?.labels || [],
                    datasets: [{
                        data: stats.category_stats?.data || [],
                        backgroundColor: [
                            '#FF6384',
                            '#36A2EB',
                            '#FFCE56',
                            '#4BC0C0',
                            '#9966FF'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }

        // 遊戲趨勢圖
        const trendCtx = document.getElementById('trendChart');
        if (trendCtx) {
            this.charts.trend = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: stats.trend_stats?.labels || [],
                    datasets: [{
                        label: '遊戲數量',
                        data: stats.trend_stats?.data || [],
                        borderColor: '#36A2EB',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }

    /**
     * 清除表單
     */
    clearForms() {
        $('form').trigger('reset');
        $('.form-control').removeClass('is-invalid');
        $('.invalid-feedback').remove();
    }
}

// 初始化管理後台
$(document).ready(() => {
    window.admin = new AdminPanel();
}); 