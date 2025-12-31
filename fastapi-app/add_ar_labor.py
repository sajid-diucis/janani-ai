# Add AR Emergency Labor Assistant to Digital Midwife tab

html_file = 'templates/index.html'

with open(html_file, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# 1. Add CSS and JS includes in the head section (before </head>)
head_includes = '''    <!-- AR Labor Assistant Styles & Scripts -->
    <link rel="stylesheet" href="/static/ar-labor.css">
    <script src="/static/ar-labor.js"></script>
'''

# Find </head> and add before it
if '</head>' in content and 'ar-labor.css' not in content:
    content = content.replace('</head>', head_includes + '</head>')
    print("✅ Added AR Labor CSS and JS includes")

# 2. Replace the existing AR Emergency Guidance section with enhanced version
old_ar_section_start = '<!-- 📱 AR EMERGENCY GUIDANCE - SECOND -->'
old_ar_section_end = '<div id="emergencyResult" style="display: none; background: rgba(255,255,255,0.95); color: #333; padding: 20px; border-radius: 15px; margin-top: 15px;"></div>'

if old_ar_section_start in content:
    # Find the section to replace
    start_idx = content.find(old_ar_section_start)
    end_idx = content.find(old_ar_section_end)
    
    if start_idx != -1 and end_idx != -1:
        end_idx = end_idx + len(old_ar_section_end) + len('</div>')
        
        # Create the enhanced AR Labor Assistant section
        new_ar_section = '''<!-- 📱 AR EMERGENCY LABOR ASSISTANT - OFFLINE FIRST -->
                <div id="ar-labor-container" style="margin-bottom: 25px;">
                    <!-- Header with status -->
                    <div class="ar-labor-header" style="display: flex; justify-content: space-between; align-items: center; padding: 20px; background: linear-gradient(135deg, #D32F2F, #B71C1C); border-radius: 15px; color: white; margin-bottom: 20px;">
                        <div>
                            <h3 style="margin: 0; font-size: 22px; display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 35px;">🏥</span> AR জরুরি প্রসব সহায়তা
                            </h3>
                            <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 13px;">Offline-First Emergency Labor Assistant</p>
                        </div>
                        <div class="ar-status-bar" style="display: flex; gap: 10px; align-items: center;">
                            <span id="ar-connectivity-status" class="connectivity-status" style="padding: 5px 12px; border-radius: 15px; font-size: 12px; background: rgba(76,175,80,0.2); color: #4CAF50;">📶 অনলাইন</span>
                            <span id="ar-battery-level" style="padding: 5px 12px; border-radius: 15px; font-size: 12px; background: rgba(255,255,255,0.1);">🔋 100%</span>
                        </div>
                    </div>
                    
                    <!-- ⚠️ CRITICAL DISCLAIMER -->
                    <div class="ar-disclaimer" style="background: rgba(255, 193, 7, 0.15); border: 2px solid #FFC107; border-radius: 12px; padding: 15px; margin-bottom: 20px; text-align: center;">
                        <p style="margin: 5px 0; color: #FFC107; font-weight: bold; font-size: 15px;">⚠️ এটি একটি সিদ্ধান্ত সহায়তা টুল। প্রশিক্ষিত ধাত্রী বা ডাক্তারের বিকল্প নয়।</p>
                        <p style="margin: 5px 0; color: #FFC107; font-size: 12px; opacity: 0.8;">⚠️ Decision Support Tool - NOT a replacement for trained medical professionals.</p>
                    </div>
                    
                    <!-- Stage Navigation -->
                    <div style="margin-bottom: 20px;">
                        <h4 style="color: #E91E63; margin-bottom: 12px; font-size: 16px;">📋 প্রসবের ধাপ নির্বাচন করুন:</h4>
                        <div class="ar-stage-nav" style="display: flex; flex-wrap: wrap; gap: 10px;">
                            <button onclick="selectARStage('preparation')" class="ar-stage-btn active" style="flex: 1; min-width: 100px; padding: 12px 8px; border: 2px solid #FFC107; background: rgba(255,193,7,0.2); color: #FFC107; border-radius: 12px; cursor: pointer;">
                                <span class="icon" style="font-size: 1.5em; display: block;">⚙️</span>
                                <span class="label" style="font-size: 12px;">প্রস্তুতি</span>
                            </button>
                            <button onclick="selectARStage('stage_1_early')" class="ar-stage-btn" style="flex: 1; min-width: 100px; padding: 12px 8px; border: 2px solid rgba(255,255,255,0.3); background: rgba(255,255,255,0.1); color: white; border-radius: 12px; cursor: pointer;">
                                <span class="icon" style="font-size: 1.5em; display: block;">⏱️</span>
                                <span class="label" style="font-size: 12px;">প্রাথমিক</span>
                            </button>
                            <button onclick="selectARStage('stage_1_active')" class="ar-stage-btn" style="flex: 1; min-width: 100px; padding: 12px 8px; border: 2px solid rgba(255,255,255,0.3); background: rgba(255,255,255,0.1); color: white; border-radius: 12px; cursor: pointer;">
                                <span class="icon" style="font-size: 1.5em; display: block;">🔄</span>
                                <span class="label" style="font-size: 12px;">সক্রিয়</span>
                            </button>
                            <button onclick="selectARStage('stage_2_crowning')" class="ar-stage-btn" style="flex: 1; min-width: 100px; padding: 12px 8px; border: 2px solid #FF5722; background: rgba(255,87,34,0.2); color: #FF5722; border-radius: 12px; cursor: pointer;">
                                <span class="icon" style="font-size: 1.5em; display: block;">👶</span>
                                <span class="label" style="font-size: 12px;">ক্রাউনিং</span>
                            </button>
                            <button onclick="selectARStage('newborn_care')" class="ar-stage-btn" style="flex: 1; min-width: 100px; padding: 12px 8px; border: 2px solid #4CAF50; background: rgba(76,175,80,0.2); color: #4CAF50; border-radius: 12px; cursor: pointer;">
                                <span class="icon" style="font-size: 1.5em; display: block;">👶💚</span>
                                <span class="label" style="font-size: 12px;">নবজাতক</span>
                            </button>
                        </div>
                    </div>
                    
                    <!-- Camera AR View (for supported devices) -->
                    <div id="ar-camera-container" style="display: none; position: relative; background: #000; border-radius: 15px; overflow: hidden; margin-bottom: 20px; aspect-ratio: 4/3;">
                        <video id="ar-video" autoplay playsinline style="width: 100%; height: 100%; object-fit: cover;"></video>
                        <canvas id="ar-canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;"></canvas>
                        <div style="position: absolute; bottom: 15px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px;">
                            <button onclick="arLabor.stopCamera()" style="padding: 10px 25px; border: none; border-radius: 25px; background: #F44336; color: white; cursor: pointer;">ক্যামেরা বন্ধ</button>
                        </div>
                    </div>
                    
                    <!-- Simplified Mode (for power save) -->
                    <div id="ar-simplified-container" style="display: none; background: rgba(255, 152, 0, 0.1); border: 2px solid #FF9800; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 20px;">
                        <p style="color: #FF9800; font-weight: bold;">🔋 ব্যাটারি সাশ্রয় মোড - সরলীকৃত নির্দেশনা</p>
                    </div>
                    
                    <!-- Instructions Display -->
                    <div id="ar-stage-header" style="display: flex; align-items: center; gap: 15px; padding: 15px 20px; border-radius: 12px; margin-bottom: 15px; background: #FFC107; color: #333;">
                        <span class="stage-icon" style="font-size: 2em;">⚙️</span>
                        <span class="stage-title" style="font-size: 1.2em; font-weight: bold;">প্রস্তুতি পর্যায়</span>
                    </div>
                    
                    <div id="ar-instructions-container" style="margin-bottom: 20px;">
                        <!-- Instructions will be loaded here -->
                        <div style="padding: 20px; background: rgba(255,255,255,0.08); border-radius: 12px; text-align: center; color: rgba(255,255,255,0.6);">
                            <p>📋 উপরের বোতাম থেকে একটি ধাপ নির্বাচন করুন</p>
                            <p style="font-size: 12px;">Select a stage above to see instructions</p>
                        </div>
                    </div>
                    
                    <!-- Contraction Timer -->
                    <div class="ar-contraction-section" style="background: rgba(233, 30, 99, 0.15); border: 2px solid #E91E63; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 20px;">
                        <h4 style="color: #E91E63; margin: 0 0 15px 0;">⏱️ সংকোচন টাইমার</h4>
                        <p style="color: rgba(255,255,255,0.7); font-size: 13px; margin-bottom: 15px;">সংকোচনের সময়কাল এবং ব্যবধান মাপুন</p>
                        <button id="contraction-timer-btn" onclick="arLabor.startContractionTimer()" style="padding: 18px 40px; border: none; border-radius: 30px; background: linear-gradient(135deg, #E91E63, #9C27B0); color: white; font-size: 1.1em; cursor: pointer;">
                            ⏱️ সংকোচন শুরু
                        </button>
                    </div>
                    
                    <!-- Camera Controls -->
                    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px;">
                        <button onclick="arLabor.startCamera()" style="flex: 1; min-width: 140px; padding: 15px; border: 2px solid #4CAF50; background: rgba(76,175,80,0.15); color: #4CAF50; border-radius: 12px; cursor: pointer; font-weight: bold;">
                            📷 ক্যামেরা চালু
                        </button>
                        <button onclick="speakCurrentInstructions()" style="flex: 1; min-width: 140px; padding: 15px; border: 2px solid #2196F3; background: rgba(33,150,243,0.15); color: #2196F3; border-radius: 12px; cursor: pointer; font-weight: bold;">
                            🔊 নির্দেশনা শুনুন
                        </button>
                    </div>
                    
                    <!-- 🚨 Emergency Protocols Section -->
                    <div class="ar-emergency-section" style="border-top: 2px solid rgba(244, 67, 54, 0.5); padding-top: 20px; margin-top: 20px;">
                        <h4 style="color: #F44336; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 1.5em;">🚨</span> জরুরি পরিস্থিতি
                        </h4>
                        <div class="ar-emergency-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px;">
                            <button onclick="showAREmergency('cord_prolapse')" style="padding: 15px; border: 2px solid #F44336; background: rgba(244,67,54,0.15); border-radius: 12px; color: white; cursor: pointer; text-align: center;">
                                <span style="font-size: 1.5em; display: block;">⚠️</span>
                                <span style="font-size: 12px;">নাড়ি বের হয়ে গেছে</span>
                            </button>
                            <button onclick="showAREmergency('shoulder_dystocia')" style="padding: 15px; border: 2px solid #F44336; background: rgba(244,67,54,0.15); border-radius: 12px; color: white; cursor: pointer; text-align: center;">
                                <span style="font-size: 1.5em; display: block;">🤝</span>
                                <span style="font-size: 12px;">কাঁধ আটকে গেছে</span>
                            </button>
                            <button onclick="showAREmergency('postpartum_hemorrhage')" style="padding: 15px; border: 2px solid #F44336; background: rgba(244,67,54,0.15); border-radius: 12px; color: white; cursor: pointer; text-align: center;">
                                <span style="font-size: 1.5em; display: block;">🩸</span>
                                <span style="font-size: 12px;">অতিরিক্ত রক্তপাত</span>
                            </button>
                            <button onclick="callEmergency()" style="padding: 15px; border: 2px solid #FF5722; background: linear-gradient(135deg, #F44336, #D32F2F); border-radius: 12px; color: white; cursor: pointer; text-align: center; font-weight: bold;">
                                <span style="font-size: 1.5em; display: block;">📞</span>
                                <span style="font-size: 14px;">৯৯৯ কল</span>
                            </button>
                        </div>
                    </div>
                    
                    <!-- Emergency Numbers Box -->
                    <div style="margin-top: 20px; background: rgba(244,67,54,0.1); border: 2px solid rgba(244,67,54,0.5); border-radius: 12px; padding: 15px;">
                        <h5 style="color: #F44336; margin: 0 0 10px 0; font-size: 14px;">📞 জরুরি যোগাযোগ নম্বর:</h5>
                        <div style="display: flex; flex-wrap: wrap; gap: 15px;">
                            <a href="tel:999" style="color: white; text-decoration: none; background: #F44336; padding: 8px 15px; border-radius: 20px; font-weight: bold;">🚨 999</a>
                            <a href="tel:199" style="color: white; text-decoration: none; background: #E91E63; padding: 8px 15px; border-radius: 20px;">🚑 199 (অ্যাম্বুলেন্স)</a>
                            <a href="tel:16789" style="color: white; text-decoration: none; background: #9C27B0; padding: 8px 15px; border-radius: 20px;">📞 16789 (স্বাস্থ্য)</a>
                        </div>
                    </div>
                </div>
                
                <!-- Modals for AR -->
                <div id="ar-emergency-modal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.95); z-index: 10000; justify-content: center; align-items: center; padding: 20px;"></div>
                <div id="ar-timer-modal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.95); z-index: 10000; justify-content: center; align-items: center;"></div>
                <div id="ar-notifications" style="position: fixed; top: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px; max-width: 350px;"></div>
'''
        
        content = content[:start_idx] + new_ar_section + content[end_idx:]
        print("✅ Replaced AR section with enhanced AR Labor Assistant")

# 3. Add AR Labor Assistant JavaScript functions before </script>
ar_js_functions = '''
        // ============ AR LABOR ASSISTANT FUNCTIONS ============
        
        let arOfflineData = null;
        let currentARStage = 'preparation';
        
        // Initialize AR Labor Assistant
        async function initARLaborAssistant() {
            try {
                // Load offline data bundle
                const response = await fetch('/api/ar-labor/offline-bundle');
                if (response.ok) {
                    const data = await response.json();
                    arOfflineData = data.bundle;
                    console.log('✅ AR offline data loaded');
                    // Load initial stage
                    selectARStage('preparation');
                }
            } catch (error) {
                console.error('Error loading AR data:', error);
            }
            
            // Setup connectivity listener
            window.addEventListener('online', () => {
                document.getElementById('ar-connectivity-status').innerHTML = '📶 অনলাইন';
                document.getElementById('ar-connectivity-status').style.background = 'rgba(76,175,80,0.2)';
                document.getElementById('ar-connectivity-status').style.color = '#4CAF50';
            });
            
            window.addEventListener('offline', () => {
                document.getElementById('ar-connectivity-status').innerHTML = '📴 অফলাইন';
                document.getElementById('ar-connectivity-status').style.background = 'rgba(244,67,54,0.2)';
                document.getElementById('ar-connectivity-status').style.color = '#F44336';
            });
            
            // Check battery
            if ('getBattery' in navigator) {
                const battery = await navigator.getBattery();
                updateBatteryDisplay(battery.level);
                battery.addEventListener('levelchange', () => updateBatteryDisplay(battery.level));
            }
        }
        
        function updateBatteryDisplay(level) {
            const percent = Math.round(level * 100);
            const el = document.getElementById('ar-battery-level');
            if (el) {
                el.innerHTML = '🔋 ' + percent + '%';
                el.style.color = percent < 20 ? '#F44336' : percent < 50 ? '#FF9800' : '#4CAF50';
            }
        }
        
        async function selectARStage(stageId) {
            currentARStage = stageId;
            
            // Update button states
            document.querySelectorAll('.ar-stage-btn').forEach(btn => {
                btn.classList.remove('active');
                btn.style.background = 'rgba(255,255,255,0.1)';
                btn.style.borderColor = 'rgba(255,255,255,0.3)';
            });
            event.target.closest('.ar-stage-btn').classList.add('active');
            event.target.closest('.ar-stage-btn').style.background = 'linear-gradient(135deg, #E91E63, #9C27B0)';
            event.target.closest('.ar-stage-btn').style.borderColor = '#E91E63';
            
            // Load stage instructions
            try {
                let stageData;
                
                if (arOfflineData && arOfflineData.stages && arOfflineData.stages[stageId]) {
                    stageData = arOfflineData.stages[stageId];
                } else {
                    const response = await fetch('/api/ar-labor/stages/' + stageId);
                    const data = await response.json();
                    stageData = data.data;
                }
                
                renderARStageInstructions(stageData);
            } catch (error) {
                console.error('Error loading stage:', error);
            }
        }
        
        function renderARStageInstructions(stage) {
            // Update header
            const header = document.getElementById('ar-stage-header');
            if (header) {
                header.innerHTML = '<span class="stage-icon" style="font-size: 2em;">' + stage.icon + '</span><span class="stage-title" style="font-size: 1.2em; font-weight: bold;">' + stage.title_bn + '</span>';
                header.style.background = stage.color;
            }
            
            // Render instructions
            const container = document.getElementById('ar-instructions-container');
            if (!container || !stage.instructions) return;
            
            let html = '<div class="ar-instructions-list" style="display: flex; flex-direction: column; gap: 12px;">';
            
            stage.instructions.forEach(inst => {
                const priorityClass = inst.audio_priority === 'critical' ? 'border-left-color: #F44336; background: rgba(244,67,54,0.1);' : 
                                     inst.audio_priority === 'high' ? 'border-left-color: #FF9800; background: rgba(255,152,0,0.1);' : 
                                     'border-left-color: #4CAF50; background: rgba(255,255,255,0.08);';
                
                html += '<div class="ar-instruction-card" style="display: flex; align-items: flex-start; gap: 15px; padding: 15px; border-radius: 12px; border-left: 4px solid #4CAF50; ' + priorityClass + '">';
                html += '<div style="width: 35px; height: 35px; border-radius: 50%; background: linear-gradient(135deg, #E91E63, #9C27B0); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; flex-shrink: 0;">' + inst.step + '</div>';
                html += '<div style="flex: 1;">';
                html += '<p style="color: white; font-size: 1.05em; margin: 0 0 5px 0; line-height: 1.5;">' + inst.text_bn + '</p>';
                html += '<p style="color: rgba(255,255,255,0.6); font-size: 0.85em; margin: 0;">' + inst.text_en + '</p>';
                html += '</div>';
                
                if (inst.timer_seconds) {
                    html += '<button onclick="startARTimer(' + inst.timer_seconds + ')" style="padding: 8px 15px; border: none; border-radius: 20px; background: rgba(255,255,255,0.15); color: white; cursor: pointer;">⏱️ ' + inst.timer_seconds + 's</button>';
                }
                
                html += '<button onclick="speakARInstruction(\\'' + inst.text_bn.replace(/'/g, "\\\\'") + '\\')" style="padding: 8px 15px; border: none; border-radius: 20px; background: rgba(255,255,255,0.15); color: white; cursor: pointer;">🔊</button>';
                html += '</div>';
            });
            
            html += '</div>';
            container.innerHTML = html;
        }
        
        function speakARInstruction(text) {
            if ('speechSynthesis' in window) {
                speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'bn-BD';
                utterance.rate = 0.9;
                speechSynthesis.speak(utterance);
            }
        }
        
        function speakCurrentInstructions() {
            // Speak all instructions for current stage
            if (arOfflineData && arOfflineData.stages && arOfflineData.stages[currentARStage]) {
                const stage = arOfflineData.stages[currentARStage];
                let fullText = stage.title_bn + '। ';
                stage.instructions.forEach(inst => {
                    fullText += 'ধাপ ' + inst.step + '। ' + inst.text_bn + '। ';
                });
                speakARInstruction(fullText);
            }
        }
        
        function startARTimer(seconds) {
            const modal = document.getElementById('ar-timer-modal');
            if (!modal) return;
            
            let remaining = seconds;
            
            modal.innerHTML = '<div style="text-align: center; padding: 40px;"><div id="ar-timer-display" style="font-size: 6em; font-weight: bold; color: #4CAF50; text-shadow: 0 0 30px rgba(76,175,80,0.5);">' + remaining + '</div><p style="color: white; font-size: 1.3em; margin: 20px 0;">সেকেন্ড বাকি</p><button onclick="stopARTimer()" style="padding: 15px 40px; border: none; border-radius: 30px; background: #F44336; color: white; font-size: 1.1em; cursor: pointer;">বন্ধ করুন</button></div>';
            modal.style.display = 'flex';
            
            window.arTimerInterval = setInterval(() => {
                remaining--;
                const display = document.getElementById('ar-timer-display');
                if (display) display.textContent = remaining;
                
                if (remaining <= 0) {
                    stopARTimer();
                    speakARInstruction('সময় শেষ!');
                }
            }, 1000);
        }
        
        function stopARTimer() {
            if (window.arTimerInterval) {
                clearInterval(window.arTimerInterval);
            }
            const modal = document.getElementById('ar-timer-modal');
            if (modal) modal.style.display = 'none';
        }
        
        async function showAREmergency(emergencyType) {
            try {
                let protocol;
                
                if (arOfflineData && arOfflineData.emergencies && arOfflineData.emergencies[emergencyType]) {
                    protocol = arOfflineData.emergencies[emergencyType];
                } else {
                    const response = await fetch('/api/ar-labor/emergencies/' + emergencyType);
                    const data = await response.json();
                    protocol = data.protocol;
                }
                
                renderEmergencyModal(protocol);
            } catch (error) {
                console.error('Error loading emergency protocol:', error);
                alert('জরুরি অবস্থায় এখনই ৯৯৯ কল করুন!');
            }
        }
        
        function renderEmergencyModal(protocol) {
            const modal = document.getElementById('ar-emergency-modal');
            if (!modal) return;
            
            let html = '<div style="max-width: 500px; width: 100%; max-height: 90vh; overflow-y: auto; border-radius: 20px; background: #1a1a2e; border: 3px solid ' + protocol.color + ';">';
            html += '<div style="padding: 20px; text-align: center; background: ' + protocol.color + '; border-radius: 17px 17px 0 0;"><h2 style="color: white; margin: 0;">' + protocol.title_bn + '</h2><p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">' + protocol.title_en + '</p></div>';
            html += '<div style="padding: 20px; text-align: center;"><a href="tel:999" style="display: inline-block; padding: 20px 40px; background: #F44336; color: white; text-decoration: none; border-radius: 30px; font-size: 1.3em; font-weight: bold; animation: pulse 1.5s infinite;">📞 এখনই ৯৯৯ কল করুন</a></div>';
            html += '<div style="padding: 20px;"><h3 style="color: white; margin-bottom: 15px;">তাৎক্ষণিক পদক্ষেপ:</h3>';
            
            protocol.immediate_actions.forEach(action => {
                html += '<div style="display: flex; align-items: flex-start; gap: 15px; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 10px; border-left: 4px solid ' + protocol.color + ';">';
                html += '<div style="width: 30px; height: 30px; border-radius: 50%; background: ' + protocol.color + '; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">' + action.step + '</div>';
                html += '<div style="flex: 1;"><p style="color: white; font-size: 1.05em; margin: 0 0 5px 0;">' + action.text_bn + '</p><p style="color: rgba(255,255,255,0.6); font-size: 0.85em; margin: 0;">' + action.text_en + '</p></div>';
                html += '<button onclick="speakARInstruction(\\'' + action.text_bn.replace(/'/g, "\\\\'") + '\\')" style="padding: 8px 15px; border: none; border-radius: 20px; background: rgba(255,255,255,0.1); color: white; cursor: pointer;">🔊</button>';
                html += '</div>';
            });
            
            html += '</div><button onclick="closeAREmergencyModal()" style="width: calc(100% - 40px); margin: 20px; padding: 15px; border: none; border-radius: 12px; background: rgba(255,255,255,0.1); color: white; cursor: pointer; font-size: 1em;">বন্ধ করুন</button></div>';
            
            modal.innerHTML = html;
            modal.style.display = 'flex';
            
            // Auto-speak first action
            if (protocol.immediate_actions.length > 0) {
                speakARInstruction(protocol.title_bn + '। ' + protocol.immediate_actions[0].text_bn);
            }
        }
        
        function closeAREmergencyModal() {
            const modal = document.getElementById('ar-emergency-modal');
            if (modal) modal.style.display = 'none';
        }
        
        function callEmergency() {
            window.location.href = 'tel:999';
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(initARLaborAssistant, 1000);
        });
        
'''

# Find the closing </script> and add before it
if '</script>' in content and 'initARLaborAssistant' not in content:
    # Find the first </script> after the main script block
    script_end_idx = content.find('</script>', content.find('<script>'))
    if script_end_idx != -1:
        content = content[:script_end_idx] + ar_js_functions + '\n    </script>'
        # Remove the duplicate </script> that will be at the end
        content = content[:script_end_idx + len(ar_js_functions) + len('\n    </script>')] + content[script_end_idx + len('</script>'):]
        print("✅ Added AR Labor Assistant JavaScript functions")

# Write the file
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ AR Emergency Labor Assistant integrated successfully!")
print("Features added:")
print("  • Phase-by-phase AR instructions in Bengali")
print("  • Emergency protocols for critical situations")
print("  • Contraction timer")
print("  • Offline-first data caching")
print("  • Battery-aware mode")
print("  • Voice instructions (TTS)")
print("  • Emergency call buttons (999, 199, 16789)")
