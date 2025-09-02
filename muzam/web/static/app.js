// MUZAM GhostKitty UI - Interactive Features
// =========================================

class MuzamUI {
    constructor() {
        this.init();
        this.createParticles();
        this.setupEventListeners();
        this.loadStats();
    }

    init() {
        console.log('🎵 MUZAM GhostKitty UI Initialized');
        this.addGhostKittyEffects();
        this.setupUploadZone();
        this.setupAudioVisualizer();
    }

    // Create floating particles background
    createParticles() {
        const particlesContainer = document.createElement('div');
        particlesContainer.className = 'particles';
        document.body.appendChild(particlesContainer);

        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 6 + 's';
            particle.style.animationDuration = (Math.random() * 3 + 6) + 's';
            particlesContainer.appendChild(particle);
        }
    }

    // Add GhostKitty floating and glow effects
    addGhostKittyEffects() {
        const ghostKitty = document.querySelector('.ghost-kitty');
        if (ghostKitty) {
            ghostKitty.addEventListener('mouseenter', () => {
                ghostKitty.style.transform = 'scale(1.2) rotate(10deg)';
                ghostKitty.style.filter = 'drop-shadow(0 0 30px rgba(138, 43, 226, 0.8))';
            });

            ghostKitty.addEventListener('mouseleave', () => {
                ghostKitty.style.transform = 'scale(1) rotate(0deg)';
                ghostKitty.style.filter = 'drop-shadow(0 0 20px rgba(138, 43, 226, 0.3))';
            });

            // Random ghost movements
            setInterval(() => {
                if (!ghostKitty.matches(':hover')) {
                    const randomX = (Math.random() - 0.5) * 20;
                    const randomY = (Math.random() - 0.5) * 10;
                    const randomRotate = (Math.random() - 0.5) * 10;
                    
                    ghostKitty.style.transform = `translate(${randomX}px, ${randomY}px) rotate(${randomRotate}deg)`;
                    
                    setTimeout(() => {
                        ghostKitty.style.transform = 'translate(0, 0) rotate(0deg)';
                    }, 2000);
                }
            }, 8000);
        }
    }

    // Enhanced upload zone with cool effects
    setupUploadZone() {
        const uploadZone = document.querySelector('.upload-zone');
        const fileInput = document.getElementById('audioFile');

        if (!uploadZone || !fileInput) return;

        // Drag and drop events
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
            this.createRippleEffect(e, uploadZone);
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });

        // Click to upload
        uploadZone.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });
    }

    // Create ripple effect on click/drag
    createRippleEffect(event, element) {
        const ripple = document.createElement('div');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: radial-gradient(circle, rgba(138, 43, 226, 0.3), transparent);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
            z-index: 1000;
        `;

        element.style.position = 'relative';
        element.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    // Handle file upload with visual feedback
    async handleFileUpload(file) {
        console.log('🎵 Uploading file:', file.name);
        
        this.showLoading('Analyzing your sick beats...');
        
        const formData = new FormData();
        formData.append('audio_file', file);
        
        try {
            const response = await fetch('/api/recognize/file', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            this.hideLoading();
            this.showResult(result);
            
        } catch (error) {
            this.hideLoading();
            this.showError('Error analyzing audio: ' + error.message);
        }
    }

    // Enhanced loading animation
    showLoading(message = 'Analyzing audio...') {
        const loadingEl = document.getElementById('loading');
        const loadingText = loadingEl.querySelector('.loading-text');
        const loadingSubtext = loadingEl.querySelector('.loading-subtext');
        
        if (loadingText) loadingText.textContent = message;
        if (loadingSubtext) loadingSubtext.textContent = 'GhostKitty is working its magic... 👻';
        
        loadingEl.classList.remove('hidden');
        this.hideResult();
        
        // Add pulsing effect to the entire page
        document.body.style.animation = 'pulse 2s ease-in-out infinite';
    }

    hideLoading() {
        const loadingEl = document.getElementById('loading');
        loadingEl.classList.add('hidden');
        document.body.style.animation = '';
    }

    // Enhanced result display with animations
    showResult(result) {
        const resultEl = document.getElementById('result');
        const resultContent = document.getElementById('resultContent');
        
        resultEl.classList.remove('hidden');
        
        if (result.success && result.result) {
            const res = result.result;
            resultContent.innerHTML = `
                <div class="result-header">
                    <div class="result-icon">🎯</div>
                    <h3 class="result-title">Track Identified!</h3>
                </div>
                <div class="result-content">
                    <div class="result-row">
                        <span class="result-label">🎵 Title</span>
                        <span class="result-value">${res.title}</span>
                    </div>
                    <div class="result-row">
                        <span class="result-label">👤 Artist</span>
                        <span class="result-value">${res.artist}</span>
                    </div>
                    ${res.album ? `
                        <div class="result-row">
                            <span class="result-label">💿 Album</span>
                            <span class="result-value">${res.album}</span>
                        </div>
                    ` : ''}
                    ${res.year ? `
                        <div class="result-row">
                            <span class="result-label">📅 Year</span>
                            <span class="result-value">${res.year}</span>
                        </div>
                    ` : ''}
                    <div class="result-row">
                        <span class="result-label">⚡ Speed</span>
                        <span class="result-value">${res.match_time.toFixed(2)}s</span>
                    </div>
                    <div class="result-row">
                        <span class="result-label">🎯 Confidence</span>
                        <span class="result-value">${(res.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${res.confidence * 100}%"></div>
                    </div>
                </div>
            `;
            
            // Trigger success celebration
            this.triggerSuccessCelebration();
            
        } else {
            resultContent.innerHTML = `
                <div class="result-header">
                    <div class="result-icon">❌</div>
                    <h3 class="result-title">No Match Found</h3>
                </div>
                <div class="result-content">
                    <p>GhostKitty couldn't identify this track. Try with a clearer recording or a different song!</p>
                    ${result.error ? `<p><strong>Error:</strong> ${result.error}</p>` : ''}
                </div>
            `;
        }
        
        // Animate result appearance
        resultEl.style.transform = 'translateY(50px)';
        resultEl.style.opacity = '0';
        
        setTimeout(() => {
            resultEl.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            resultEl.style.transform = 'translateY(0)';
            resultEl.style.opacity = '1';
        }, 100);
        
        this.loadStats();
    }

    hideResult() {
        const resultEl = document.getElementById('result');
        resultEl.classList.add('hidden');
    }

    showError(message) {
        this.showResult({
            success: false,
            error: message
        });
    }

    // Success celebration with visual effects
    triggerSuccessCelebration() {
        // Create confetti effect
        for (let i = 0; i < 30; i++) {
            setTimeout(() => {
                this.createConfetti();
            }, i * 50);
        }
        
        // Flash the background briefly
        document.body.style.background = 'linear-gradient(45deg, #8a2be2, #00ffff, #39ff14)';
        setTimeout(() => {
            document.body.style.background = '';
        }, 200);
        
        // Make GhostKitty dance
        const ghostKitty = document.querySelector('.ghost-kitty');
        if (ghostKitty) {
            ghostKitty.style.animation = 'ghostDance 0.5s ease-in-out 3';
        }
    }

    createConfetti() {
        const confetti = document.createElement('div');
        const colors = ['#8a2be2', '#00ffff', '#39ff14', '#ff4500', '#dc143c'];
        const color = colors[Math.floor(Math.random() * colors.length)];
        
        confetti.style.cssText = `
            position: fixed;
            top: -10px;
            left: ${Math.random() * window.innerWidth}px;
            width: 8px;
            height: 8px;
            background: ${color};
            z-index: 10000;
            pointer-events: none;
            border-radius: 50%;
            animation: confettiFall 3s ease-out forwards;
        `;
        
        document.body.appendChild(confetti);
        
        setTimeout(() => {
            confetti.remove();
        }, 3000);
    }

    // Microphone recording with visual feedback
    async startMicrophoneRecording() {
        console.log('🎤 Starting microphone recording...');
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                await this.recognizeAudioBlob(audioBlob);
            };
            
            this.mediaRecorder.start();
            
            // Visual recording feedback
            this.showRecordingUI();
            
            // Auto-stop after 10 seconds
            setTimeout(() => {
                if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                    this.stopRecording();
                }
            }, 10000);
            
        } catch (error) {
            this.showError('Microphone access denied or not available');
        }
    }

    showRecordingUI() {
        const recordBtn = document.querySelector('[onclick="startMicrophoneRecording()"]');
        const stopBtn = document.getElementById('stopBtn');
        
        if (recordBtn) {
            recordBtn.style.display = 'none';
        }
        if (stopBtn) {
            stopBtn.style.display = 'inline-block';
        }
        
        this.showLoading('Listening to your environment... 🎧');
        
        // Add recording pulse effect
        const recordingIndicator = document.createElement('div');
        recordingIndicator.id = 'recordingIndicator';
        recordingIndicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            width: 20px;
            height: 20px;
            background: #dc143c;
            border-radius: 50%;
            animation: recordingPulse 1s ease-in-out infinite;
            z-index: 10000;
        `;
        document.body.appendChild(recordingIndicator);
    }

    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            // Reset UI
            const recordBtn = document.querySelector('[onclick="startMicrophoneRecording()"]');
            const stopBtn = document.getElementById('stopBtn');
            
            if (recordBtn) recordBtn.style.display = 'inline-block';
            if (stopBtn) stopBtn.style.display = 'none';
            
            // Remove recording indicator
            const indicator = document.getElementById('recordingIndicator');
            if (indicator) indicator.remove();
        }
    }

    async recognizeAudioBlob(blob) {
        const formData = new FormData();
        formData.append('audio_file', blob, 'recording.wav');
        
        try {
            const response = await fetch('/api/recognize/file', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            this.hideLoading();
            this.showResult(result);
        } catch (error) {
            this.hideLoading();
            this.showError('Error recognizing audio: ' + error.message);
        }
    }

    // Load and display stats with animations
    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            this.animateStatValues('totalSongs', stats.total_songs);
            this.animateStatValues('totalRecognitions', stats.total_recognitions);
            this.animateStatValues('accuracy', '95.7'); // Placeholder
            
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    animateStatValues(elementId, finalValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const duration = 2000;
        const startValue = 0;
        const increment = finalValue / (duration / 50);
        let currentValue = startValue;
        
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                currentValue = finalValue;
                clearInterval(timer);
            }
            
            if (elementId === 'accuracy') {
                element.textContent = currentValue.toFixed(1) + '%';
            } else {
                element.textContent = Math.floor(currentValue).toLocaleString();
            }
        }, 50);
    }

    // Setup audio visualizer (placeholder for future enhancement)
    setupAudioVisualizer() {
        // TODO: Add real-time audio visualization
        console.log('🎵 Audio visualizer ready');
    }

    // Setup all event listeners
    setupEventListeners() {
        // Add custom CSS animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes ghostDance {
                0%, 100% { transform: rotate(0deg) scale(1); }
                25% { transform: rotate(-5deg) scale(1.1); }
                75% { transform: rotate(5deg) scale(1.1); }
            }
            
            @keyframes confettiFall {
                0% { transform: translateY(-10px) rotate(0deg); opacity: 1; }
                100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
            }
            
            @keyframes recordingPulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.5; transform: scale(0.8); }
            }
            
            @keyframes ripple {
                to { transform: scale(2); opacity: 0; }
            }
            
            @keyframes pulse {
                0%, 100% { filter: brightness(1); }
                50% { filter: brightness(1.1); }
            }
        `;
        document.head.appendChild(style);
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'u':
                        e.preventDefault();
                        document.getElementById('audioFile').click();
                        break;
                    case 'r':
                        e.preventDefault();
                        this.startMicrophoneRecording();
                        break;
                }
            }
        });
    }
}

// Global functions for HTML onclick handlers
function startMicrophoneRecording() {
    window.muzamUI.startMicrophoneRecording();
}

function stopRecording() {
    window.muzamUI.stopRecording();
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.muzamUI = new MuzamUI();
    console.log('👻 GhostKitty MUZAM UI is ready to rock!');
});
