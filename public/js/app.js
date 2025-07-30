/**
 * 🎮 英文對答遊戲 - 主要 JavaScript 檔案
 * 使用 jQuery 和 Bootstrap 5
 */

class EnglishGame {
    constructor() {
        this.apiBase = 'http://localhost:5000/api';
        this.socket = null;
        this.token = localStorage.getItem('token');
        this.currentUser = null;
        this.currentRoom = null;
        this.currentQuestion = null;
        this.gameTimer = null;
        this.timeLeft = 30;
        
        this.init();
    }

    /**
     * 初始化應用程式
     */
    init() {
        this.setupEventListeners();
        this.checkAuthStatus();
        this.connectSocket();
        this.loadCategories();
    }

    /**
     * 設定事件監聽器
     */
    setupEventListeners() {
        // 導航事件
        $('#loginBtn, #navbarLoginBtn').on('click', () => this.showLoginModal());
        $('#registerBtn, #navbarRegisterBtn').on('click', () => this.showRegisterModal());
        $('#logoutBtn').on('click', () => this.logout());
        
        // 表單提交事件
        $('#loginForm').on('submit', (e) => {
            e.preventDefault();
            this.login();
        });
        
        $('#registerForm').on('submit', (e) => {
            e.preventDefault();
            this.register();
        });
        
        // 房間相關事件
        $('#createRoomBtn').on('click', () => this.showCreateRoomModal());
        $('#createRoomForm').on('submit', (e) => {
            e.preventDefault();
            this.createRoom();
        });
        
        // 遊戲相關事件
        $('#startGameBtn').on('click', () => this.startGame());
        $('#nextRoundBtn').on('click', () => this.nextRound());
        $('#leaveRoomBtn').on('click', () => this.leaveRoom());
        
        // 聊天事件
        $('#chatForm').on('submit', (e) => {
            e.preventDefault();
            this.sendChatMessage();
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
            this.showLoginSection();
        }
    }

    /**
     * 連接 WebSocket
     */
    connectSocket() {
        if (this.socket) {
            this.socket.disconnect();
        }
        
        this.socket = io('http://localhost:5000');
        
        this.socket.on('connect', () => {
            console.log('WebSocket 已連線');
            this.showNotification('WebSocket 已連線', 'success');
        });
        
        this.socket.on('disconnect', () => {
            console.log('WebSocket 已斷線');
            this.showNotification('WebSocket 已斷線', 'warning');
        });
        
        this.socket.on('player_joined_socket', (data) => {
            this.handlePlayerJoined(data);
        });
        
        this.socket.on('player_left_socket', (data) => {
            this.handlePlayerLeft(data);
        });
        
        this.socket.on('game_started', (data) => {
            this.handleGameStarted(data);
        });
        
        this.socket.on('question_updated', (data) => {
            this.handleQuestionUpdated(data);
        });
        
        this.socket.on('answer_submitted', (data) => {
            this.handleAnswerSubmitted(data);
        });
        
        this.socket.on('round_ended', (data) => {
            this.handleRoundEnded(data);
        });
        
        this.socket.on('game_ended', (data) => {
            this.handleGameEnded(data);
        });
        
        this.socket.on('chat_message', (data) => {
            this.handleChatMessage(data);
        });
        
        this.socket.on('error', (data) => {
            this.showNotification(data.message, 'error');
        });
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
     * 載入分類
     */
    async loadCategories() {
        try {
            const data = await this.apiRequest('/questions/categories');
            this.populateCategorySelects(data.categories);
        } catch (error) {
            console.error('載入分類失敗:', error);
        }
    }

    /**
     * 填充分類選擇器
     */
    populateCategorySelects(categories) {
        const options = categories.map(category => 
            `<option value="${category}">${category}</option>`
        ).join('');
        
        $('.category-select').html(options);
    }

    /**
     * 顯示登入區塊
     */
    showLoginSection() {
        $('#authSection').show();
        $('#gameSection').hide();
        $('#userSection').hide();
    }

    /**
     * 顯示遊戲區塊
     */
    showGameSection() {
        $('#authSection').hide();
        $('#gameSection').show();
        $('#userSection').show();
    }

    /**
     * 顯示登入模態框
     */
    showLoginModal() {
        $('#loginModal').modal('show');
    }

    /**
     * 顯示註冊模態框
     */
    showRegisterModal() {
        $('#registerModal').modal('show');
    }

    /**
     * 登入
     */
    async login() {
        const formData = {
            username: $('#loginUsername').val(),
            password: $('#loginPassword').val()
        };
        
        try {
            this.showLoading('#loginSubmitBtn');
            const data = await this.apiRequest('/auth/login', {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            
            this.token = data.access_token;
            this.currentUser = data.user;
            localStorage.setItem('token', this.token);
            
            this.showNotification('登入成功！', 'success');
            $('#loginModal').modal('hide');
            this.showGameSection();
            this.updateUserInfo();
            
        } catch (error) {
            console.error('登入失敗:', error);
        } finally {
            this.hideLoading('#loginSubmitBtn');
        }
    }

    /**
     * 註冊
     */
    async register() {
        const formData = {
            username: $('#registerUsername').val(),
            email: $('#registerEmail').val(),
            password: $('#registerPassword').val()
        };
        
        try {
            this.showLoading('#registerSubmitBtn');
            await this.apiRequest('/auth/register', {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            
            this.showNotification('註冊成功！請登入', 'success');
            $('#registerModal').modal('hide');
            this.showLoginModal();
            
        } catch (error) {
            console.error('註冊失敗:', error);
        } finally {
            this.hideLoading('#registerSubmitBtn');
        }
    }

    /**
     * 取得當前使用者資訊
     */
    async getCurrentUser() {
        try {
            const data = await this.apiRequest('/auth/me');
            this.currentUser = data.user;
            this.showGameSection();
            this.updateUserInfo();
        } catch (error) {
            console.error('取得使用者資訊失敗:', error);
            this.logout();
        }
    }

    /**
     * 更新使用者資訊顯示
     */
    updateUserInfo() {
        if (this.currentUser) {
            $('#userInfo').html(`
                <span class="navbar-text">
                    <i class="fas fa-user"></i> ${this.currentUser.username}
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
        this.currentRoom = null;
        localStorage.removeItem('token');
        
        if (this.socket) {
            this.socket.disconnect();
        }
        
        this.showLoginSection();
        this.showNotification('已登出', 'info');
    }

    /**
     * 顯示建立房間模態框
     */
    showCreateRoomModal() {
        $('#createRoomModal').modal('show');
    }

    /**
     * 建立房間
     */
    async createRoom() {
        const formData = {
            name: $('#roomName').val(),
            max_players: parseInt($('#maxPlayers').val()),
            total_rounds: parseInt($('#totalRounds').val()),
            categories: $('#roomCategories').val().split(',').filter(c => c.trim())
        };
        
        try {
            this.showLoading('#createRoomSubmitBtn');
            const data = await this.apiRequest('/rooms', {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            
            this.currentRoom = data.room;
            this.showNotification('房間建立成功！', 'success');
            $('#createRoomModal').modal('hide');
            this.joinRoom(this.currentRoom.id);
            
        } catch (error) {
            console.error('建立房間失敗:', error);
        } finally {
            this.hideLoading('#createRoomSubmitBtn');
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
            <div class="room-item" onclick="game.joinRoom('${room.id}')">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h5 class="mb-1">${room.name}</h5>
                        <p class="mb-1 text-muted">
                            <i class="fas fa-users"></i> ${room.current_players}/${room.max_players} 玩家
                            <span class="mx-2">|</span>
                            <i class="fas fa-gamepad"></i> ${room.current_round}/${room.total_rounds} 回合
                        </p>
                    </div>
                    <span class="room-status ${room.status}">${this.getStatusText(room.status)}</span>
                </div>
            </div>
        `).join('');
        
        $('#roomsList').html(roomsHtml);
    }

    /**
     * 取得狀態文字
     */
    getStatusText(status) {
        const statusMap = {
            'waiting': '等待中',
            'in_progress': '進行中',
            'finished': '已結束'
        };
        return statusMap[status] || status;
    }

    /**
     * 加入房間
     */
    async joinRoom(roomId) {
        try {
            const data = await this.apiRequest(`/rooms/${roomId}/join`, {
                method: 'POST'
            });
            
            this.currentRoom = data.room;
            this.showNotification('成功加入房間！', 'success');
            this.showRoomInterface();
            
            // 加入 WebSocket 房間
            if (this.socket) {
                this.socket.emit('join_room', {
                    room_id: roomId,
                    token: this.token
                });
            }
            
        } catch (error) {
            console.error('加入房間失敗:', error);
        }
    }

    /**
     * 顯示房間介面
     */
    showRoomInterface() {
        $('#roomsSection').hide();
        $('#roomInterface').show();
        this.updateRoomInfo();
        this.loadRoomPlayers();
    }

    /**
     * 更新房間資訊
     */
    updateRoomInfo() {
        if (this.currentRoom) {
            $('#roomName').text(this.currentRoom.name);
            $('#roomStatus').text(this.getStatusText(this.currentRoom.status));
            $('#roomPlayers').text(`${this.currentRoom.current_players}/${this.currentRoom.max_players}`);
            $('#roomRounds').text(`${this.currentRoom.current_round}/${this.currentRoom.total_rounds}`);
        }
    }

    /**
     * 載入房間玩家
     */
    async loadRoomPlayers() {
        if (!this.currentRoom) return;
        
        try {
            const data = await this.apiRequest(`/rooms/${this.currentRoom.id}/players`);
            this.displayPlayers(data.players);
        } catch (error) {
            console.error('載入玩家失敗:', error);
        }
    }

    /**
     * 顯示玩家列表
     */
    displayPlayers(players) {
        const playersHtml = players.map(player => `
            <div class="player-item">
                <div class="player-avatar">
                    ${player.username.charAt(0).toUpperCase()}
                </div>
                <div class="player-info">
                    <div class="player-name">${player.username}</div>
                    <div class="player-score">分數: ${player.score || 0}</div>
                </div>
            </div>
        `).join('');
        
        $('#playersList').html(playersHtml);
    }

    /**
     * 開始遊戲
     */
    async startGame() {
        if (!this.currentRoom) return;
        
        try {
            this.showLoading('#startGameBtn');
            await this.apiRequest(`/rooms/${this.currentRoom.id}/start`, {
                method: 'POST'
            });
            
            this.showNotification('遊戲開始！', 'success');
            
        } catch (error) {
            console.error('開始遊戲失敗:', error);
        } finally {
            this.hideLoading('#startGameBtn');
        }
    }

    /**
     * 下一回合
     */
    async nextRound() {
        if (!this.currentRoom) return;
        
        try {
            this.showLoading('#nextRoundBtn');
            await this.apiRequest(`/rooms/${this.currentRoom.id}/next-round`, {
                method: 'POST'
            });
            
        } catch (error) {
            console.error('下一回合失敗:', error);
        } finally {
            this.hideLoading('#nextRoundBtn');
        }
    }

    /**
     * 離開房間
     */
    async leaveRoom() {
        if (!this.currentRoom) return;
        
        try {
            await this.apiRequest(`/rooms/${this.currentRoom.id}/leave`, {
                method: 'POST'
            });
            
            this.currentRoom = null;
            this.showNotification('已離開房間', 'info');
            this.showRoomsSection();
            
        } catch (error) {
            console.error('離開房間失敗:', error);
        }
    }

    /**
     * 顯示房間列表區塊
     */
    showRoomsSection() {
        $('#roomInterface').hide();
        $('#roomsSection').show();
        this.loadRooms();
    }

    /**
     * 載入當前題目
     */
    async loadCurrentQuestion() {
        if (!this.currentRoom) return;
        
        try {
            const data = await this.apiRequest(`/game/${this.currentRoom.id}/current-question`);
            this.displayQuestion(data.question);
            this.startTimer();
        } catch (error) {
            console.error('載入題目失敗:', error);
        }
    }

    /**
     * 顯示題目
     */
    displayQuestion(question) {
        this.currentQuestion = question;
        
        const questionHtml = `
            <div class="question-card">
                <div class="question-text">${question.question_text}</div>
                <div class="options-container">
                    ${question.options.map((option, index) => `
                        <button class="option-btn" onclick="game.selectAnswer('${option}')">
                            ${String.fromCharCode(65 + index)}. ${option}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
        
        $('#questionContainer').html(questionHtml);
    }

    /**
     * 選擇答案
     */
    selectAnswer(answer) {
        if (!this.currentQuestion) return;
        
        // 移除其他選項的選中狀態
        $('.option-btn').removeClass('selected');
        
        // 選中當前選項
        $(`.option-btn:contains('${answer}')`).addClass('selected');
        
        // 提交答案
        this.submitAnswer(answer);
    }

    /**
     * 提交答案
     */
    async submitAnswer(answer) {
        if (!this.currentRoom || !this.currentQuestion) return;
        
        const timeTaken = 30 - this.timeLeft;
        
        try {
            const data = await this.apiRequest(`/game/${this.currentRoom.id}/submit-answer`, {
                method: 'POST',
                body: JSON.stringify({
                    answer: answer,
                    time_taken: timeTaken
                })
            });
            
            this.showAnswerResult(data.is_correct, data.correct_answer, data.explanation);
            
        } catch (error) {
            console.error('提交答案失敗:', error);
        }
    }

    /**
     * 顯示答案結果
     */
    showAnswerResult(isCorrect, correctAnswer, explanation) {
        const resultText = isCorrect ? '答對了！' : '答錯了！';
        
        // 更新選項樣式
        $('.option-btn').each(function() {
            const optionText = $(this).text().split('. ')[1];
            if (optionText === correctAnswer) {
                $(this).addClass('correct');
            } else if ($(this).hasClass('selected') && !isCorrect) {
                $(this).addClass('incorrect');
            }
        });
        
        // 顯示詳細結果
        const resultHtml = `
            <div class="text-center">
                <div class="mb-3">
                    <i class="fas fa-${isCorrect ? 'check-circle text-success' : 'times-circle text-danger'} fa-3x"></i>
                </div>
                <h4 class="${isCorrect ? 'text-success' : 'text-danger'}">
                    ${resultText}
                </h4>
                <p class="text-muted">正確答案：${correctAnswer}</p>
                ${explanation ? `<p class="text-info"><i class="fas fa-lightbulb me-1"></i>${explanation}</p>` : ''}
                <div class="mt-3">
                    <button class="btn btn-primary" onclick="game.waitForNextRound()">
                        <i class="fas fa-clock me-1"></i>等待其他玩家
                    </button>
                </div>
            </div>
        `;
        
        $('#questionContainer').html(resultHtml);
        this.showNotification(resultText, isCorrect ? 'success' : 'error');
        this.stopTimer();
    }

    /**
     * 等待下一回合
     */
    waitForNextRound() {
        const waitingHtml = `
            <div class="text-center">
                <div class="mb-3">
                    <i class="fas fa-clock fa-3x text-primary"></i>
                </div>
                <h4 class="text-primary">等待其他玩家...</h4>
                <p class="text-muted">其他玩家還在答題中</p>
                <div class="progress">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" style="width: 100%"></div>
                </div>
            </div>
        `;
        
        $('#questionContainer').html(waitingHtml);
    }

    /**
     * 開始計時器
     */
    startTimer() {
        this.timeLeft = 30;
        this.updateTimer();
        
        this.gameTimer = setInterval(() => {
            this.timeLeft--;
            this.updateTimer();
            
            if (this.timeLeft <= 0) {
                this.stopTimer();
                this.showNotification('時間到！', 'warning');
            } else if (this.timeLeft <= 10) {
                $('#timerContainer').addClass('timer-warning');
            }
        }, 1000);
    }

    /**
     * 停止計時器
     */
    stopTimer() {
        if (this.gameTimer) {
            clearInterval(this.gameTimer);
            this.gameTimer = null;
        }
        $('#timerContainer').removeClass('timer-warning');
    }

    /**
     * 更新計時器顯示
     */
    updateTimer() {
        $('#timerContainer').text(`⏰ ${this.timeLeft} 秒`);
    }

    /**
     * 發送聊天訊息
     */
    sendChatMessage() {
        const message = $('#chatInput').val().trim();
        if (!message) return;
        
        if (this.socket && this.currentRoom) {
            this.socket.emit('send_message', {
                room_id: this.currentRoom.id,
                message: message,
                token: this.token
            });
        }
        
        $('#chatInput').val('');
    }

    /**
     * 顯示載入狀態
     */
    showLoading(selector) {
        $(selector).prop('disabled', true).html('<span class="loading-spinner"></span> 載入中...');
    }

    /**
     * 隱藏載入狀態
     */
    hideLoading(selector) {
        $(selector).prop('disabled', false).html($(selector).data('original-text') || '確定');
    }

    /**
     * 清除表單
     */
    clearForms() {
        $('form').trigger('reset');
        $('.form-control').removeClass('is-invalid');
        $('.invalid-feedback').remove();
    }

    // WebSocket 事件處理器
    handlePlayerJoined(data) {
        this.showNotification(`${data.username} 加入了房間`, 'info');
        this.loadRoomPlayers();
    }

    handlePlayerLeft(data) {
        this.showNotification(`${data.username} 離開了房間`, 'info');
        this.loadRoomPlayers();
    }

    handleGameStarted(data) {
        this.showNotification('遊戲開始！', 'success');
        this.updateRoomInfo();
        this.loadCurrentQuestion();
    }

    handleQuestionUpdated(data) {
        this.displayQuestion(data.question);
    }

    handleAnswerSubmitted(data) {
        this.showNotification(`${data.username} 已回答題目`, 'info');
    }

    handleRoundEnded(data) {
        this.showNotification('回合結束！', 'info');
        this.stopTimer();
        this.updateRoomInfo();
    }

    handleGameEnded(data) {
        this.showNotification('遊戲結束！', 'info');
        this.stopTimer();
        this.updateRoomInfo();
        this.loadRoomPlayers();
        this.showGameResults(data.rankings);
    }

    /**
     * 顯示遊戲結果
     */
    showGameResults(rankings) {
        const resultsHtml = `
            <div class="text-center">
                <div class="mb-4">
                    <i class="fas fa-trophy fa-3x text-warning"></i>
                </div>
                <h3 class="text-warning mb-4">遊戲結束！</h3>
                
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>排名</th>
                                        <th>玩家</th>
                                        <th>分數</th>
                                        <th>正確率</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${rankings.map((player, index) => `
                                        <tr class="${index === 0 ? 'table-warning' : ''}">
                                            <td>
                                                ${index === 0 ? '<i class="fas fa-crown text-warning"></i>' : ''}
                                                ${player.rank}
                                            </td>
                                            <td>${player.username}</td>
                                            <td>${player.score}</td>
                                            <td>${player.accuracy}%</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <div class="mt-4">
                    <button class="btn btn-primary me-2" onclick="game.returnToLobby()">
                        <i class="fas fa-home me-1"></i>返回大廳
                    </button>
                    <button class="btn btn-success" onclick="game.playAgain()">
                        <i class="fas fa-redo me-1"></i>再玩一次
                    </button>
                </div>
            </div>
        `;
        
        $('#questionContainer').html(resultsHtml);
    }

    /**
     * 返回大廳
     */
    returnToLobby() {
        this.currentRoom = null;
        this.showRoomsSection();
    }

    /**
     * 再玩一次
     */
    playAgain() {
        if (this.currentRoom) {
            this.joinRoom(this.currentRoom.id);
        }
    }

    handleChatMessage(data) {
        const messageHtml = `
            <div class="chat-message ${data.user_id === this.currentUser?.id ? 'sent' : 'received'}">
                <strong>${data.username}:</strong> ${data.message}
            </div>
        `;
        
        $('#chatMessages').append(messageHtml);
        $('#chatMessages').scrollTop($('#chatMessages')[0].scrollHeight);
    }
}

// 初始化應用程式
$(document).ready(() => {
    window.game = new EnglishGame();
}); 