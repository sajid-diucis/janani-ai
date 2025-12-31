# Script to add JavaScript functions for Digital Midwife
import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# JavaScript functions to add
js_functions = '''
        // ===== DIGITAL MIDWIFE FUNCTIONS =====
        
        let triageRecording = false;
        let triageMediaRecorder;
        let triageAudioChunks = [];
        
        // Setup maternal profile
        async function setupMidwifeProfile() {
            const week = parseInt(document.getElementById('midwifeGestationalWeek').value);
            const age = parseInt(document.getElementById('midwifeAge').value);
            const gravida = parseInt(document.getElementById('midwifeGravida').value);
            
            const riskFactors = [];
            if (document.getElementById('risk_hypertension').checked) riskFactors.push('hypertension');
            if (document.getElementById('risk_diabetes').checked) riskFactors.push('diabetes');
            if (document.getElementById('risk_anemia').checked) riskFactors.push('anemia');
            if (document.getElementById('risk_previous_csection').checked) riskFactors.push('previous_cesarean');
            
            try {
                const response = await fetch('/api/midwife/profile', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        user_id: 'web_user_midwife',
                        gestational_week: week,
                        age: age,
                        gravida: gravida,
                        para: gravida > 1 ? gravida - 1 : 0,
                        blood_type: 'unknown',
                        risk_factors: riskFactors,
                        medications: [],
                        previous_complications: [],
                        preferred_hospital: 'nearest'
                    })
                });
                
                const data = await response.json();
                alert('✅ প্রোফাইল সেভ হয়েছে! ঝুঁকির স্তর: ' + (data.risk_level || 'নির্ধারিত'));
            } catch (error) {
                alert('❌ সমস্যা হয়েছে: ' + error.message);
            }
        }
        
        // Get weekly care plan
        async function getWeeklyCarePlan() {
            const week = parseInt(document.getElementById('midwifeGestationalWeek').value);
            const resultDiv = document.getElementById('carePlanResult');
            
            resultDiv.innerHTML = '<p style="text-align: center;">⏳ লোড হচ্ছে...</p>';
            resultDiv.style.display = 'block';
            
            try {
                const response = await fetch(`/api/midwife/care-plan/web_user_midwife/week/${week}`);
                const data = await response.json();
                
                let html = `
                    <div style="margin-bottom: 15px;">
                        <h4 style="color: #9C27B0; margin-bottom: 10px;">📅 সপ্তাহ ${data.week} - ${data.trimester}</h4>
                    </div>
                    
                    <div style="background: #f3e5f5; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
                        <strong>👶 শিশুর অবস্থা:</strong>
                        <p style="margin: 8px 0 0 0; font-size: 14px;">${data.baby_development || 'এই সপ্তাহে শিশুর বিকাশ চলছে'}</p>
                    </div>
                    
                    <div style="background: #e8f5e9; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
                        <strong>🍎 পুষ্টি নির্দেশিকা:</strong>
                        <ul style="margin: 8px 0 0 0; font-size: 14px; padding-left: 20px;">
                            ${(data.nutrition_guidelines || ['সুষম খাবার খান']).map(n => `<li>${n}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
                        <strong>🏥 ডাক্তারের চেকআপ:</strong>
                        <ul style="margin: 8px 0 0 0; font-size: 14px; padding-left: 20px;">
                            ${(data.anc_checklist || ['নিয়মিত চেকআপ করুন']).map(c => `<li>${c}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div style="background: #fff3e0; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
                        <strong>🏃‍♀️ ব্যায়াম:</strong>
                        <ul style="margin: 8px 0 0 0; font-size: 14px; padding-left: 20px;">
                            ${(data.exercises || ['হালকা হাঁটাচলা করুন']).map(e => `<li>${e}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div style="background: #ffebee; padding: 12px; border-radius: 8px;">
                        <strong>⚠️ সতর্কতা চিহ্ন:</strong>
                        <ul style="margin: 8px 0 0 0; font-size: 14px; padding-left: 20px; color: #c62828;">
                            ${(data.warning_signs || ['অস্বাভাবিক কিছু হলে ডাক্তার দেখান']).map(w => `<li>${w}</li>`).join('')}
                        </ul>
                    </div>
                `;
                
                resultDiv.innerHTML = html;
            } catch (error) {
                resultDiv.innerHTML = `<p style="color: red;">❌ সমস্যা: ${error.message}</p>`;
            }
        }
        
        // Triage voice recording
        async function toggleTriageVoice() {
            if (!triageRecording) {
                await startTriageRecording();
            } else {
                stopTriageRecording();
            }
        }
        
        async function startTriageRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                triageMediaRecorder = new MediaRecorder(stream);
                triageAudioChunks = [];
                
                triageMediaRecorder.ondataavailable = event => {
                    triageAudioChunks.push(event.data);
                };
                
                triageMediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(triageAudioChunks, { type: 'audio/wav' });
                    await processTriageAudio(audioBlob);
                };
                
                triageMediaRecorder.start();
                triageRecording = true;
                document.getElementById('triageVoiceBtn').style.background = 'linear-gradient(135deg, #f44336, #c62828)';
                document.getElementById('triageVoiceBtn').innerHTML = '⏹️';
                document.getElementById('triageVoiceStatus').textContent = '🔴 রেকর্ডিং চলছে... থামাতে আবার চাপুন';
            } catch (error) {
                alert('মাইক্রোফোন অ্যাক্সেস করতে পারছি না: ' + error.message);
            }
        }
        
        function stopTriageRecording() {
            if (triageMediaRecorder && triageMediaRecorder.state === 'recording') {
                triageMediaRecorder.stop();
                triageMediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
            triageRecording = false;
            document.getElementById('triageVoiceBtn').style.background = 'linear-gradient(135deg, #4CAF50, #2E7D32)';
            document.getElementById('triageVoiceBtn').innerHTML = '🎤';
            document.getElementById('triageVoiceStatus').textContent = 'প্রসেসিং হচ্ছে...';
        }
        
        async function processTriageAudio(audioBlob) {
            try {
                const formData = new FormData();
                formData.append('file', audioBlob, 'triage_audio.wav');
                
                // First transcribe
                const transcribeResponse = await fetch('/api/voice/transcribe', {
                    method: 'POST',
                    body: formData
                });
                const transcribeData = await transcribeResponse.json();
                
                if (transcribeData.text) {
                    document.getElementById('triageTextInput').value = transcribeData.text;
                    document.getElementById('triageVoiceStatus').textContent = 'টেক্সট পাওয়া গেছে। বিশ্লেষণ করতে বোতাম চাপুন।';
                    performTriage();
                }
            } catch (error) {
                document.getElementById('triageVoiceStatus').textContent = 'সমস্যা হয়েছে: ' + error.message;
            }
        }
        
        // Perform triage analysis
        async function performTriage() {
            const symptoms = document.getElementById('triageTextInput').value;
            const resultDiv = document.getElementById('triageResult');
            
            if (!symptoms.trim()) {
                alert('দয়া করে আপনার সমস্যা বলুন বা লিখুন');
                return;
            }
            
            resultDiv.innerHTML = '<p style="color: white; text-align: center;">⏳ বিশ্লেষণ হচ্ছে...</p>';
            resultDiv.style.display = 'block';
            
            const week = parseInt(document.getElementById('midwifeGestationalWeek').value) || 20;
            
            try {
                const response = await fetch('/api/midwife/triage', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        user_id: 'web_user_midwife',
                        symptoms_description: symptoms,
                        gestational_week: week,
                        dialect: 'standard_bangla'
                    })
                });
                
                const data = await response.json();
                
                let severityColor = '#4CAF50'; // Green for low
                let severityBg = '#e8f5e9';
                if (data.severity === 'HIGH' || data.severity === 'CRITICAL') {
                    severityColor = '#f44336';
                    severityBg = '#ffebee';
                } else if (data.severity === 'MODERATE') {
                    severityColor = '#FF9800';
                    severityBg = '#fff3e0';
                }
                
                let html = `
                    <div style="background: ${severityBg}; color: #333; padding: 15px; border-radius: 10px; border-left: 5px solid ${severityColor};">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                            <span style="font-size: 24px;">${data.severity === 'CRITICAL' ? '🚨' : data.severity === 'HIGH' ? '⚠️' : data.severity === 'MODERATE' ? '⚡' : '✅'}</span>
                            <strong style="color: ${severityColor}; font-size: 18px;">ঝুঁকির স্তর: ${data.severity || 'LOW'}</strong>
                        </div>
                        
                        <p style="margin-bottom: 10px;"><strong>সনাক্ত করা সমস্যা:</strong> ${(data.detected_symptoms || []).join(', ') || 'সাধারণ'}</p>
                        
                        <div style="margin-bottom: 10px;">
                            <strong>পরামর্শ:</strong>
                            <ul style="margin: 5px 0 0 20px;">
                                ${(data.recommendations || ['বিশ্রাম নিন']).map(r => `<li>${r}</li>`).join('')}
                            </ul>
                        </div>
                        
                        ${data.requires_immediate_care ? '<p style="color: #f44336; font-weight: bold; margin-top: 10px;">🚨 এখনই ডাক্তার দেখান!</p>' : ''}
                        
                        <p style="margin-top: 10px; font-size: 12px; color: #666;"><em>⏱️ পরবর্তী পদক্ষেপ: ${data.next_step || 'নির্দেশনা অনুসরণ করুন'}</em></p>
                    </div>
                `;
                
                resultDiv.innerHTML = html;
            } catch (error) {
                resultDiv.innerHTML = `<p style="color: white;">❌ সমস্যা: ${error.message}</p>`;
            }
        }
        
        // Emergency activation
        async function activateEmergency(emergencyType) {
            const resultDiv = document.getElementById('emergencyResult');
            
            resultDiv.innerHTML = '<p style="text-align: center;">⏳ জরুরি সেবা সক্রিয় হচ্ছে...</p>';
            resultDiv.style.display = 'block';
            
            try {
                const response = await fetch('/api/midwife/emergency/activate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        user_id: 'web_user_midwife',
                        emergency_type: emergencyType,
                        current_location: {latitude: 23.8103, longitude: 90.4125}, // Dhaka default
                        symptoms_description: emergencyType
                    })
                });
                
                const data = await response.json();
                
                let html = `
                    <div style="margin-bottom: 15px;">
                        <h4 style="color: #c62828; margin-bottom: 10px;">🚨 ${data.emergency_type_bn || emergencyType}</h4>
                    </div>
                    
                    <div style="background: #fff3e0; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
                        <strong>📞 জরুরি নম্বর:</strong>
                        <p style="font-size: 24px; font-weight: bold; color: #f44336; margin: 10px 0;">${data.emergency_hotline || '999'}</p>
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
                        <strong>🏥 নিকটতম হাসপাতাল:</strong>
                        <p style="margin: 8px 0 0 0;">${data.nearest_hospital?.name || 'Dhaka Medical College'}</p>
                        <p style="font-size: 14px; color: #666;">${data.nearest_hospital?.address || 'ঢাকা'}</p>
                    </div>
                    
                    <div style="background: #ffebee; padding: 12px; border-radius: 8px;">
                        <strong>⚡ এখনই করুন:</strong>
                        <ol style="margin: 8px 0 0 20px; font-size: 14px;">
                            ${(data.immediate_steps || ['শান্ত থাকুন', '999 কল করুন']).map(s => `<li>${s}</li>`).join('')}
                        </ol>
                    </div>
                `;
                
                resultDiv.innerHTML = html;
                
                // Optionally speak the emergency instructions
                if (data.voice_message) {
                    speakEmergencyMessage(data.voice_message);
                }
            } catch (error) {
                resultDiv.innerHTML = `<p style="color: red;">❌ সমস্যা: ${error.message}</p>`;
            }
        }
        
        async function speakEmergencyMessage(message) {
            try {
                const response = await fetch('/api/voice/speak', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: message, language: 'bn'})
                });
                
                if (response.ok) {
                    const audioBlob = await response.blob();
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audio = new Audio(audioUrl);
                    audio.play();
                }
            } catch (error) {
                console.log('Voice message not available');
            }
        }
        
        // ===== END DIGITAL MIDWIFE FUNCTIONS =====

'''

# Find where to insert (before "// Initialize")
insert_marker = '// Initialize'
insert_index = content.find(insert_marker)

if insert_index != -1:
    new_content = content[:insert_index] + js_functions + '\n        ' + content[insert_index:]
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ JavaScript functions added successfully!")
else:
    print("❌ Could not find insertion point")
