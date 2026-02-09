# Reorder Digital Midwife tab - Voice Triage first
import re

with open('templates/index.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Find the midwife-tab content
midwife_start = content.find('<div id="midwife-tab"')
if midwife_start == -1:
    print("Could not find midwife-tab")
    exit()

# Find where the tab ends (next tab or end of container)
midwife_end = content.find('</div>\n    <script>', midwife_start)
if midwife_end == -1:
    midwife_end = content.find('</div>\n        \n    <script>', midwife_start)

print(f"Found midwife tab from {midwife_start} to {midwife_end}")

# Create new midwife tab content with Voice Triage FIRST
new_midwife_content = '''<div id="midwife-tab" class="tab-content">
            <div class="card">
                <div style="text-align: center; margin-bottom: 25px;">
                    <h2 style="color: #E91E63; margin-bottom: 10px;">🤰 ডিজিটাল মিডওয়াইফ</h2>
                    <p style="color: #666;">AI-চালিত মাতৃত্ব যত্ন সহকারী - WHO নির্দেশিকা অনুযায়ী</p>
                </div>

                <!-- 🎤 VOICE TRIAGE - FIRST AND MOST PROMINENT -->
                <div style="background: linear-gradient(135deg, #1565C0, #0D47A1); padding: 25px; border-radius: 20px; margin-bottom: 25px; color: white; box-shadow: 0 8px 32px rgba(21, 101, 192, 0.3);">
                    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
                        <span style="font-size: 40px;">🎤</span>
                        <div>
                            <h3 style="margin: 0; font-size: 24px;">কথা বলে স্বাস্থ্য পরীক্ষা</h3>
                            <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;">Voice Triage - আপনার সমস্যা বাংলায় বলুন</p>
                        </div>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; margin-bottom: 20px;">
                        <div style="display: flex; align-items: center; gap: 20px;">
                            <button id="triageVoiceBtn" onclick="toggleTriageVoice()" style="width: 100px; height: 100px; border-radius: 50%; border: 4px solid white; background: linear-gradient(135deg, #4CAF50, #2E7D32); color: white; font-size: 40px; cursor: pointer; box-shadow: 0 6px 20px rgba(0,0,0,0.3); flex-shrink: 0; transition: all 0.3s;">
                                🎤
                            </button>
                            <div style="flex: 1;">
                                <p id="triageVoiceStatus" style="margin: 0 0 15px 0; font-size: 16px; font-weight: bold;">👆 মাইক বোতামে চাপুন এবং আপনার সমস্যা বলুন</p>
                                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                                    <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; font-size: 12px;">🗣️ বাংলায় বলুন</span>
                                    <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; font-size: 12px;">🔍 AI বিশ্লেষণ</span>
                                    <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; font-size: 12px;">⚡ তাৎক্ষণিক ফলাফল</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 8px; font-size: 14px;">অথবা টাইপ করুন:</label>
                        <input type="text" id="triageTextInput" placeholder="যেমন: 'মাথা ব্যথা হচ্ছে', 'পা ফুলে গেছে', 'রক্তপাত হচ্ছে'..." style="width: 100%; padding: 15px; border-radius: 10px; border: none; font-size: 16px; color: #333;">
                    </div>
                    
                    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px;">
                        <span style="font-size: 13px; opacity: 0.8;">দ্রুত নির্বাচন:</span>
                        <button onclick="document.getElementById('triageTextInput').value='মাথা ব্যথা করছে'" style="background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.5); color: white; padding: 6px 12px; border-radius: 15px; cursor: pointer; font-size: 12px;">মাথা ব্যথা</button>
                        <button onclick="document.getElementById('triageTextInput').value='পেটে ব্যথা হচ্ছে'" style="background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.5); color: white; padding: 6px 12px; border-radius: 15px; cursor: pointer; font-size: 12px;">পেটে ব্যথা</button>
                        <button onclick="document.getElementById('triageTextInput').value='পা ফুলে গেছে'" style="background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.5); color: white; padding: 6px 12px; border-radius: 15px; cursor: pointer; font-size: 12px;">পা ফোলা</button>
                        <button onclick="document.getElementById('triageTextInput').value='রক্তপাত হচ্ছে'" style="background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.5); color: white; padding: 6px 12px; border-radius: 15px; cursor: pointer; font-size: 12px;">রক্তপাত</button>
                        <button onclick="document.getElementById('triageTextInput').value='বাচ্চা নড়ছে না'" style="background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.5); color: white; padding: 6px 12px; border-radius: 15px; cursor: pointer; font-size: 12px;">বাচ্চা নড়ছে না</button>
                    </div>
                    
                    <button onclick="performTriage()" style="width: 100%; padding: 16px; background: linear-gradient(135deg, #FF9800, #F57C00); color: white; border: none; border-radius: 12px; font-size: 18px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(255, 152, 0, 0.4);">
                        🔍 বিশ্লেষণ করুন
                    </button>
                    
                    <div id="triageResult" style="margin-top: 20px; display: none;"></div>
                </div>

                <!-- 📱 AR EMERGENCY GUIDANCE - SECOND -->
                <div style="background: linear-gradient(135deg, #D32F2F, #B71C1C); padding: 25px; border-radius: 20px; margin-bottom: 25px; color: white; box-shadow: 0 8px 32px rgba(211, 47, 47, 0.3);">
                    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
                        <span style="font-size: 40px;">📱</span>
                        <div>
                            <h3 style="margin: 0; font-size: 24px;">AR জরুরি গাইড</h3>
                            <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;">Augmented Reality - ক্যামেরায় দেখুন কি করতে হবে</p>
                        </div>
                    </div>
                    
                    <p style="margin-bottom: 20px; opacity: 0.9;">জরুরি অবস্থায় AR নির্দেশিকা দেখুন - ছবি ও অ্যানিমেশন সহ</p>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 20px;">
                        <button onclick="showARGuide('hemorrhage')" style="padding: 20px 15px; background: rgba(255,255,255,0.15); border: 2px solid rgba(255,255,255,0.5); border-radius: 15px; color: white; cursor: pointer; text-align: center; transition: all 0.3s;">
                            <div style="font-size: 32px; margin-bottom: 8px;">🩸</div>
                            <div style="font-weight: bold;">রক্তপাত</div>
                            <div style="font-size: 11px; opacity: 0.8; margin-top: 4px;">Hemorrhage</div>
                        </button>
                        <button onclick="showARGuide('labor')" style="padding: 20px 15px; background: rgba(255,255,255,0.15); border: 2px solid rgba(255,255,255,0.5); border-radius: 15px; color: white; cursor: pointer; text-align: center; transition: all 0.3s;">
                            <div style="font-size: 32px; margin-bottom: 8px;">👶</div>
                            <div style="font-weight: bold;">প্রসব</div>
                            <div style="font-size: 11px; opacity: 0.8; margin-top: 4px;">Labor</div>
                        </button>
                        <button onclick="showARGuide('eclampsia')" style="padding: 20px 15px; background: rgba(255,255,255,0.15); border: 2px solid rgba(255,255,255,0.5); border-radius: 15px; color: white; cursor: pointer; text-align: center; transition: all 0.3s;">
                            <div style="font-size: 32px; margin-bottom: 8px;">⚡</div>
                            <div style="font-weight: bold;">খিঁচুনি</div>
                            <div style="font-size: 11px; opacity: 0.8; margin-top: 4px;">Eclampsia</div>
                        </button>
                        <button onclick="showARGuide('breathing')" style="padding: 20px 15px; background: rgba(255,255,255,0.15); border: 2px solid rgba(255,255,255,0.5); border-radius: 15px; color: white; cursor: pointer; text-align: center; transition: all 0.3s;">
                            <div style="font-size: 32px; margin-bottom: 8px;">💨</div>
                            <div style="font-weight: bold;">শ্বাসকষ্ট</div>
                            <div style="font-size: 11px; opacity: 0.8; margin-top: 4px;">Breathing</div>
                        </button>
                        <button onclick="showARGuide('fetal_movement')" style="padding: 20px 15px; background: rgba(255,255,255,0.15); border: 2px solid rgba(255,255,255,0.5); border-radius: 15px; color: white; cursor: pointer; text-align: center; transition: all 0.3s;">
                            <div style="font-size: 32px; margin-bottom: 8px;">👣</div>
                            <div style="font-weight: bold;">বাচ্চার নড়াচড়া</div>
                            <div style="font-size: 11px; opacity: 0.8; margin-top: 4px;">Fetal Movement</div>
                        </button>
                        <button onclick="activateEmergency('general')" style="padding: 20px 15px; background: rgba(255,255,255,0.15); border: 2px solid rgba(255,255,255,0.5); border-radius: 15px; color: white; cursor: pointer; text-align: center; transition: all 0.3s;">
                            <div style="font-size: 32px; margin-bottom: 8px;">🆘</div>
                            <div style="font-weight: bold;">জরুরি কল</div>
                            <div style="font-size: 11px; opacity: 0.8; margin-top: 4px;">Emergency</div>
                        </button>
                    </div>
                    
                    <div id="arGuideResult" style="display: none; background: rgba(255,255,255,0.95); color: #333; padding: 20px; border-radius: 15px;"></div>
                    <div id="emergencyResult" style="display: none; background: rgba(255,255,255,0.95); color: #333; padding: 20px; border-radius: 15px; margin-top: 15px;"></div>
                </div>

                <!-- Profile Setup - Compact -->
                <div style="background: linear-gradient(135deg, #7B1FA2, #6A1B9A); padding: 20px; border-radius: 15px; margin-bottom: 20px; color: white;">
                    <h3 style="margin: 0 0 15px 0;">📋 আপনার প্রোফাইল</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px;">
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-size: 13px;">গর্ভকালীন সপ্তাহ</label>
                            <input type="number" id="midwifeGestationalWeek" value="20" min="1" max="42" style="width: 100%; padding: 10px; border-radius: 8px; border: none; color: #333;">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-size: 13px;">বয়স</label>
                            <input type="number" id="midwifeAge" value="25" min="15" max="50" style="width: 100%; padding: 10px; border-radius: 8px; border: none; color: #333;">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-size: 13px;">গর্ভধারণ</label>
                            <select id="midwifeGravida" style="width: 100%; padding: 10px; border-radius: 8px; border: none; color: #333;">
                                <option value="1">প্রথম</option>
                                <option value="2">দ্বিতীয়</option>
                                <option value="3">তৃতীয়+</option>
                            </select>
                        </div>
                    </div>
                    <div style="margin-top: 12px; display: flex; flex-wrap: wrap; gap: 8px;">
                        <label style="display: flex; align-items: center; gap: 5px; background: rgba(255,255,255,0.2); padding: 6px 10px; border-radius: 6px; font-size: 12px; cursor: pointer;">
                            <input type="checkbox" id="risk_hypertension"> উচ্চ রক্তচাপ
                        </label>
                        <label style="display: flex; align-items: center; gap: 5px; background: rgba(255,255,255,0.2); padding: 6px 10px; border-radius: 6px; font-size: 12px; cursor: pointer;">
                            <input type="checkbox" id="risk_diabetes"> ডায়াবেটিস
                        </label>
                        <label style="display: flex; align-items: center; gap: 5px; background: rgba(255,255,255,0.2); padding: 6px 10px; border-radius: 6px; font-size: 12px; cursor: pointer;">
                            <input type="checkbox" id="risk_anemia"> রক্তস্বল্পতা
                        </label>
                    </div>
                </div>

                <!-- Weekly Care Plan - Compact -->
                <div style="background: linear-gradient(135deg, #00796B, #004D40); padding: 20px; border-radius: 15px; margin-bottom: 20px; color: white;">
                    <h3 style="margin: 0 0 15px 0;">📅 সাপ্তাহিক যত্ন পরিকল্পনা</h3>
                    <p style="opacity: 0.9; margin-bottom: 15px; font-size: 14px;">আপনার গর্ভকালীন সপ্তাহ অনুযায়ী WHO নির্দেশিকা</p>
                    <button onclick="getWeeklyCarePlan()" style="width: 100%; padding: 14px; background: white; color: #00796B; border: none; border-radius: 10px; font-weight: bold; font-size: 16px; cursor: pointer;">
                        📋 এই সপ্তাহের পরিকল্পনা দেখুন
                    </button>
                    <div id="carePlanResult" style="margin-top: 15px; display: none; background: rgba(255,255,255,0.95); color: #333; padding: 15px; border-radius: 10px; max-height: 400px; overflow-y: auto;"></div>
                </div>

                <!-- Red Flag Warning Signs -->
                <div style="background: linear-gradient(135deg, #FF5722, #E64A19); padding: 20px; border-radius: 15px; color: white;">
                    <h3 style="margin: 0 0 15px 0;">⚠️ বিপদ চিহ্ন - এগুলো দেখলে এখনই ডাক্তার দেখান</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                        <div style="background: rgba(255,255,255,0.2); padding: 12px; border-radius: 8px; font-size: 14px;">🩸 হঠাৎ রক্তপাত</div>
                        <div style="background: rgba(255,255,255,0.2); padding: 12px; border-radius: 8px; font-size: 14px;">💧 পানি ভাঙা</div>
                        <div style="background: rgba(255,255,255,0.2); padding: 12px; border-radius: 8px; font-size: 14px;">🤕 তীব্র মাথাব্যথা</div>
                        <div style="background: rgba(255,255,255,0.2); padding: 12px; border-radius: 8px; font-size: 14px;">🦵 পা/মুখ ফোলা</div>
                        <div style="background: rgba(255,255,255,0.2); padding: 12px; border-radius: 8px; font-size: 14px;">👶 বাচ্চা নড়ছে না</div>
                        <div style="background: rgba(255,255,255,0.2); padding: 12px; border-radius: 8px; font-size: 14px;">⚡ খিঁচুনি</div>
                    </div>
                </div>
            </div>
        </div>
'''

# Find the end of the old midwife tab content
# Look for the closing </div> before the script section
old_content = content[midwife_start:]
# Find where this tab's content ends
depth = 0
end_pos = 0
for i, char in enumerate(old_content):
    if old_content[i:i+4] == '<div':
        depth += 1
    elif old_content[i:i+6] == '</div>':
        depth -= 1
        if depth == 0:
            end_pos = i + 6
            break

# If we found the end, replace
if end_pos > 0:
    actual_end = midwife_start + end_pos
    new_content = content[:midwife_start] + new_midwife_content + content[actual_end:]
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Digital Midwife tab reordered! Voice Triage is now FIRST!")
else:
    print("Could not find end of midwife tab")
