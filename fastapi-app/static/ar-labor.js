/**
 * AR Emergency Labor Assistant - Main JavaScript Module
 * Offline-First Medical Emergency Tool for Rural Bangladesh
 * 
 * ⚠️ DISCLAIMER: This is a DECISION SUPPORT TOOL. 
 * It is NOT a replacement for a trained midwife or doctor.
 */

class ARLaborAssistant {
    constructor() {
        this.currentStage = 'preparation';
        this.offlineData = null;
        this.sessionLog = [];
        this.isOnline = navigator.onLine;
        this.batteryLevel = 100;
        this.powerSaveMode = false;
        this.poseDetector = null;
        this.cameraStream = null;
        this.db = null;
        
        this.init();
    }
    
    async init() {
        console.log('🤰 Initializing AR Labor Assistant...');
        
        // Setup offline detection
        this.setupConnectivityListener();
        
        // Setup battery monitoring
        await this.setupBatteryMonitor();
        
        // Initialize IndexedDB
        await this.initIndexedDB();
        
        // Load offline data
        await this.loadOfflineBundle();
        
        // Register service worker
        await this.registerServiceWorker();
        
        console.log('✅ AR Labor Assistant initialized');
    }
    
    // ============ Connectivity Management ============
    
    setupConnectivityListener() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            console.log('📶 Online - syncing data...');
            this.showConnectivityStatus('online');
            this.syncOfflineData();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            console.log('📴 Offline - using cached data');
            this.showConnectivityStatus('offline');
        });
    }
    
    showConnectivityStatus(status) {
        const statusEl = document.getElementById('ar-connectivity-status');
        if (statusEl) {
            if (status === 'online') {
                statusEl.innerHTML = '📶 অনলাইন';
                statusEl.className = 'connectivity-status online';
            } else {
                statusEl.innerHTML = '📴 অফলাইন';
                statusEl.className = 'connectivity-status offline';
            }
        }
    }
    
    // ============ Battery Management ============
    
    async setupBatteryMonitor() {
        if ('getBattery' in navigator) {
            try {
                const battery = await navigator.getBattery();
                this.batteryLevel = Math.round(battery.level * 100);
                
                battery.addEventListener('levelchange', () => {
                    this.batteryLevel = Math.round(battery.level * 100);
                    this.checkPowerSaveMode();
                });
                
                this.checkPowerSaveMode();
            } catch (e) {
                console.log('Battery API not available');
            }
        }
    }
    
    checkPowerSaveMode() {
        const previousMode = this.powerSaveMode;
        this.powerSaveMode = this.batteryLevel < 20;
        
        if (this.powerSaveMode !== previousMode) {
            if (this.powerSaveMode) {
                console.log('🔋 Power Save Mode enabled');
                this.showPowerSaveNotification();
                this.switchToSimplifiedMode();
            } else {
                console.log('🔋 Normal mode restored');
            }
        }
        
        this.updateBatteryDisplay();
    }
    
    updateBatteryDisplay() {
        const batteryEl = document.getElementById('ar-battery-level');
        if (batteryEl) {
            const color = this.batteryLevel < 20 ? '#F44336' : 
                         this.batteryLevel < 50 ? '#FF9800' : '#4CAF50';
            batteryEl.innerHTML = `🔋 ${this.batteryLevel}%`;
            batteryEl.style.color = color;
        }
    }
    
    showPowerSaveNotification() {
        this.showNotification(
            '🔋 ব্যাটারি কম',
            'ব্যাটারি সাশ্রয় মোড চালু হয়েছে। সরলীকৃত নির্দেশনা দেখানো হবে।',
            'warning'
        );
    }
    
    switchToSimplifiedMode() {
        // Stop camera/AR processing
        this.stopCamera();
        
        // Switch to 2D illustrations
        const arContainer = document.getElementById('ar-camera-container');
        if (arContainer) {
            arContainer.style.display = 'none';
        }
        
        const simplifiedContainer = document.getElementById('ar-simplified-container');
        if (simplifiedContainer) {
            simplifiedContainer.style.display = 'block';
        }
    }
    
    // ============ IndexedDB Setup ============
    
    async initIndexedDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('JananiARLabor', 1);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve();
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                if (!db.objectStoreNames.contains('session_logs')) {
                    db.createObjectStore('session_logs', { keyPath: 'id', autoIncrement: true });
                }
                if (!db.objectStoreNames.contains('offline_data')) {
                    db.createObjectStore('offline_data', { keyPath: 'key' });
                }
                if (!db.objectStoreNames.contains('contractions')) {
                    db.createObjectStore('contractions', { keyPath: 'id', autoIncrement: true });
                }
            };
        });
    }
    
    // ============ Offline Data Management ============
    
    async loadOfflineBundle() {
        try {
            // Try to load from server first
            if (this.isOnline) {
                const response = await fetch('/api/ar-labor/offline-bundle');
                if (response.ok) {
                    const data = await response.json();
                    this.offlineData = data.bundle;
                    await this.cacheOfflineData(this.offlineData);
                    console.log('✅ Offline data loaded from server');
                    return;
                }
            }
            
            // Fall back to cached data
            this.offlineData = await this.getCachedOfflineData();
            if (this.offlineData) {
                console.log('📦 Using cached offline data');
            }
        } catch (error) {
            console.error('Error loading offline bundle:', error);
            // Use hardcoded emergency data as last resort
            this.offlineData = this.getEmergencyFallbackData();
        }
    }
    
    async cacheOfflineData(data) {
        if (!this.db) return;
        
        const tx = this.db.transaction('offline_data', 'readwrite');
        const store = tx.objectStore('offline_data');
        
        store.put({
            key: 'ar_labor_offline_data',
            data: data,
            timestamp: new Date().toISOString()
        });
        
        // Also cache in service worker
        if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
            navigator.serviceWorker.controller.postMessage({
                type: 'CACHE_OFFLINE_DATA',
                data: data
            });
        }
    }
    
    async getCachedOfflineData() {
        if (!this.db) return null;
        
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('offline_data', 'readonly');
            const store = tx.objectStore('offline_data');
            const request = store.get('ar_labor_offline_data');
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                resolve(request.result?.data || null);
            };
        });
    }
    
    getEmergencyFallbackData() {
        // Hardcoded critical emergency data for when nothing else works
        return {
            emergency_numbers: {
                bangladesh_999: '999',
                ambulance: '199',
                health_helpline: '16789'
            },
            disclaimer: {
                text_bn: '⚠️ এটি একটি সিদ্ধান্ত সহায়তা টুল। জরুরি অবস্থায় ৯৯৯ কল করুন।',
                text_en: '⚠️ This is a decision support tool. Call 999 in emergencies.'
            }
        };
    }
    
    // ============ Service Worker ============
    
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/ar-labor-sw.js');
                console.log('✅ Service Worker registered');
                
                // Listen for sync complete messages
                navigator.serviceWorker.addEventListener('message', (event) => {
                    if (event.data.type === 'SYNC_COMPLETE') {
                        this.showNotification(
                            '✅ ডেটা সিঙ্ক হয়েছে',
                            `${event.data.count}টি এন্ট্রি সার্ভারে পাঠানো হয়েছে`,
                            'success'
                        );
                    }
                });
            } catch (error) {
                console.error('Service Worker registration failed:', error);
            }
        }
    }
    
    // ============ Session Logging ============
    
    async logAction(action, details = {}) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            action: action,
            stage: this.currentStage,
            details: details,
            synced: false
        };
        
        this.sessionLog.push(logEntry);
        
        // Save to IndexedDB
        if (this.db) {
            const tx = this.db.transaction('session_logs', 'readwrite');
            const store = tx.objectStore('session_logs');
            store.add(logEntry);
        }
        
        // Try to sync if online
        if (this.isOnline) {
            this.syncOfflineData();
        }
        
        return logEntry;
    }
    
    async syncOfflineData() {
        if ('serviceWorker' in navigator && 'sync' in window.registration) {
            try {
                await window.registration.sync.register('sync-session-log');
            } catch (e) {
                // Fallback: direct sync
                this.directSync();
            }
        } else {
            this.directSync();
        }
    }
    
    async directSync() {
        if (!this.db || !this.isOnline) return;
        
        try {
            const tx = this.db.transaction('session_logs', 'readonly');
            const store = tx.objectStore('session_logs');
            const request = store.getAll();
            
            request.onsuccess = async () => {
                const logs = request.result.filter(l => !l.synced);
                if (logs.length === 0) return;
                
                const response = await fetch('/api/ar-labor/sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_log: logs,
                        device_id: this.getDeviceId(),
                        timestamp: new Date().toISOString()
                    })
                });
                
                if (response.ok) {
                    console.log('✅ Data synced successfully');
                }
            };
        } catch (error) {
            console.error('Sync failed:', error);
        }
    }
    
    getDeviceId() {
        let deviceId = localStorage.getItem('janani_device_id');
        if (!deviceId) {
            deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('janani_device_id', deviceId);
        }
        return deviceId;
    }
    
    // ============ Stage Navigation ============
    
    setStage(stageId) {
        this.currentStage = stageId;
        this.logAction('stage_changed', { new_stage: stageId });
        this.renderStageInstructions(stageId);
    }
    
    renderStageInstructions(stageId) {
        if (!this.offlineData || !this.offlineData.stages) {
            console.error('No offline data available');
            return;
        }
        
        const stage = this.offlineData.stages[stageId];
        if (!stage) {
            console.error('Stage not found:', stageId);
            return;
        }
        
        const container = document.getElementById('ar-instructions-container');
        if (!container) return;
        
        // Update header
        const header = document.getElementById('ar-stage-header');
        if (header) {
            header.innerHTML = `
                <span class="stage-icon">${stage.icon}</span>
                <span class="stage-title">${stage.title_bn}</span>
            `;
            header.style.backgroundColor = stage.color;
        }
        
        // Render instructions
        let html = '<div class="ar-instructions-list">';
        
        stage.instructions.forEach((inst, index) => {
            const priorityClass = inst.audio_priority === 'critical' ? 'critical' : 
                                 inst.audio_priority === 'high' ? 'high' : 'normal';
            
            html += `
                <div class="ar-instruction-card ${priorityClass}" data-step="${inst.step}">
                    <div class="instruction-step">${inst.step}</div>
                    <div class="instruction-content">
                        <p class="instruction-text-bn">${inst.text_bn}</p>
                        <p class="instruction-text-en">${inst.text_en}</p>
                    </div>
                    ${inst.timer_seconds ? `
                        <button class="timer-btn" onclick="arLabor.startTimer(${inst.timer_seconds})">
                            ⏱️ ${inst.timer_seconds}s
                        </button>
                    ` : ''}
                    <button class="speak-btn" onclick="arLabor.speakInstruction('${inst.text_bn.replace(/'/g, "\\'")}')">
                        🔊
                    </button>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
    }
    
    // ============ Emergency Protocols ============
    
    showEmergencyProtocol(emergencyType) {
        this.logAction('emergency_activated', { type: emergencyType });
        
        if (!this.offlineData || !this.offlineData.emergencies) {
            this.showNotification('⚠️ ত্রুটি', 'জরুরি ডেটা লোড হয়নি। ৯৯৯ কল করুন।', 'error');
            return;
        }
        
        const protocol = this.offlineData.emergencies[emergencyType];
        if (!protocol) {
            console.error('Emergency protocol not found:', emergencyType);
            return;
        }
        
        // Show emergency modal
        const modal = document.getElementById('ar-emergency-modal');
        if (!modal) return;
        
        let html = `
            <div class="emergency-modal-content" style="background: ${protocol.color}20; border: 3px solid ${protocol.color}">
                <div class="emergency-header" style="background: ${protocol.color}">
                    <h2>${protocol.title_bn}</h2>
                    <p>${protocol.title_en}</p>
                </div>
                
                <div class="emergency-call-btn">
                    <a href="tel:999" class="call-999-btn">
                        📞 এখনই ৯৯৯ কল করুন
                    </a>
                </div>
                
                <div class="emergency-actions">
                    <h3>তাৎক্ষণিক পদক্ষেপ:</h3>
        `;
        
        protocol.immediate_actions.forEach((action) => {
            html += `
                <div class="emergency-action-card">
                    <div class="action-step">${action.step}</div>
                    <div class="action-content">
                        <p class="action-bn">${action.text_bn}</p>
                        <p class="action-en">${action.text_en}</p>
                    </div>
                    <button class="speak-btn" onclick="arLabor.speakInstruction('${action.text_bn.replace(/'/g, "\\'")}')">
                        🔊
                    </button>
                </div>
            `;
        });
        
        html += `
                </div>
                <button class="close-emergency-btn" onclick="arLabor.closeEmergencyModal()">
                    বন্ধ করুন
                </button>
            </div>
        `;
        
        modal.innerHTML = html;
        modal.style.display = 'flex';
        
        // Auto-speak first instruction
        if (protocol.immediate_actions.length > 0) {
            this.speakInstruction(protocol.immediate_actions[0].text_bn);
        }
    }
    
    closeEmergencyModal() {
        const modal = document.getElementById('ar-emergency-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    // ============ Timer Functions ============
    
    startTimer(seconds) {
        this.logAction('timer_started', { duration: seconds });
        
        const timerModal = document.getElementById('ar-timer-modal');
        if (!timerModal) return;
        
        let remaining = seconds;
        
        timerModal.innerHTML = `
            <div class="timer-modal-content">
                <div class="timer-display" id="timer-display">${remaining}</div>
                <p class="timer-label">সেকেন্ড বাকি</p>
                <button class="timer-stop-btn" onclick="arLabor.stopTimer()">বন্ধ করুন</button>
            </div>
        `;
        timerModal.style.display = 'flex';
        
        this.timerInterval = setInterval(() => {
            remaining--;
            const display = document.getElementById('timer-display');
            if (display) {
                display.textContent = remaining;
            }
            
            if (remaining <= 5 && remaining > 0) {
                // Beep warning
                this.playBeep();
            }
            
            if (remaining <= 0) {
                this.stopTimer();
                this.speakInstruction('সময় শেষ!');
                this.showNotification('⏱️ সময় শেষ!', 'টাইমার সম্পন্ন হয়েছে', 'success');
            }
        }, 1000);
    }
    
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        const timerModal = document.getElementById('ar-timer-modal');
        if (timerModal) {
            timerModal.style.display = 'none';
        }
    }
    
    playBeep() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            oscillator.type = 'sine';
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.connect(audioContext.destination);
            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.1);
        } catch (e) {
            console.log('Audio not available');
        }
    }
    
    // ============ Speech Functions ============
    
    speakInstruction(text) {
        if ('speechSynthesis' in window) {
            // Cancel any ongoing speech
            speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'bn-BD';
            utterance.rate = 0.9;
            utterance.pitch = 1;
            
            // Try to find Bengali voice
            const voices = speechSynthesis.getVoices();
            const bengaliVoice = voices.find(v => v.lang.includes('bn'));
            if (bengaliVoice) {
                utterance.voice = bengaliVoice;
            }
            
            speechSynthesis.speak(utterance);
        }
    }
    
    // ============ Contraction Timer ============
    
    startContractionTimer() {
        this.contractionStart = new Date();
        this.logAction('contraction_started');
        
        const btn = document.getElementById('contraction-timer-btn');
        if (btn) {
            btn.innerHTML = '🔴 সংকোচন শেষ';
            btn.onclick = () => this.endContractionTimer();
            btn.classList.add('active');
        }
    }
    
    endContractionTimer() {
        const end = new Date();
        const duration = Math.round((end - this.contractionStart) / 1000);
        
        this.logAction('contraction_ended', { duration_seconds: duration });
        
        // Save to IndexedDB
        if (this.db) {
            const tx = this.db.transaction('contractions', 'readwrite');
            const store = tx.objectStore('contractions');
            store.add({
                start_time: this.contractionStart.toISOString(),
                end_time: end.toISOString(),
                duration_seconds: duration
            });
        }
        
        const btn = document.getElementById('contraction-timer-btn');
        if (btn) {
            btn.innerHTML = '⏱️ সংকোচন শুরু';
            btn.onclick = () => this.startContractionTimer();
            btn.classList.remove('active');
        }
        
        this.showNotification(
            '⏱️ সংকোচন রেকর্ড হয়েছে',
            `সময়কাল: ${duration} সেকেন্ড`,
            'info'
        );
    }
    
    // ============ Camera / AR Functions ============
    
    async startCamera() {
        if (this.powerSaveMode) {
            this.showNotification(
                '🔋 ব্যাটারি কম',
                'ক্যামেরা বন্ধ আছে ব্যাটারি বাঁচাতে',
                'warning'
            );
            return;
        }
        
        try {
            const video = document.getElementById('ar-video');
            if (!video) return;
            
            this.cameraStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment', width: 640, height: 480 }
            });
            
            video.srcObject = this.cameraStream;
            await video.play();
            
            this.logAction('camera_started');
            
            // Initialize pose detection if available
            await this.initPoseDetection();
            
        } catch (error) {
            console.error('Camera error:', error);
            this.showNotification(
                '📷 ক্যামেরা ত্রুটি',
                'ক্যামেরা অ্যাক্সেস করা যাচ্ছে না',
                'error'
            );
        }
    }
    
    stopCamera() {
        if (this.cameraStream) {
            this.cameraStream.getTracks().forEach(track => track.stop());
            this.cameraStream = null;
        }
        
        const video = document.getElementById('ar-video');
        if (video) {
            video.srcObject = null;
        }
        
        this.logAction('camera_stopped');
    }
    
    async initPoseDetection() {
        // MediaPipe pose detection initialization
        // This would use @mediapipe/pose library
        console.log('Pose detection would initialize here with MediaPipe');
        
        // For now, show simplified overlay guidance
        this.showPositionGuide();
    }
    
    showPositionGuide() {
        const canvas = document.getElementById('ar-canvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Draw position guide overlay
        ctx.fillStyle = 'rgba(76, 175, 80, 0.3)';
        ctx.fillRect(100, 200, 200, 150); // Green zone example
        
        ctx.fillStyle = 'white';
        ctx.font = '14px Arial';
        ctx.fillText('সবুজ জোন - সঠিক অবস্থান', 110, 280);
    }
    
    // ============ Notification System ============
    
    showNotification(title, message, type = 'info') {
        const container = document.getElementById('ar-notifications');
        if (!container) return;
        
        const colors = {
            info: '#2196F3',
            success: '#4CAF50',
            warning: '#FF9800',
            error: '#F44336'
        };
        
        const notification = document.createElement('div');
        notification.className = `ar-notification ${type}`;
        notification.style.borderLeftColor = colors[type];
        notification.innerHTML = `
            <strong>${title}</strong>
            <p>${message}</p>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
}

// Global instance
let arLabor = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if AR Labor section exists
    if (document.getElementById('ar-labor-container')) {
        arLabor = new ARLaborAssistant();
    }
});

// Export for global access
window.ARLaborAssistant = ARLaborAssistant;
window.arLabor = arLabor;
