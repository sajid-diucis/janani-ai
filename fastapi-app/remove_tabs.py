# Remove voice chat and prescription tabs
import re

with open('templates/index.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# 1. Update tabs - remove voice and prescription buttons, make food or midwife active
old_tabs = '''        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('voice')">🎤 ভয়েস চ্যাট</button>
            <button class="tab-btn" onclick="showTab('prescription')">💊 প্রেসক্রিপশন</button>
            <button class="tab-btn" onclick="showTab('food')">🍎 খাদ্য বিশ্লেষণ</button>
            <button class="tab-btn" onclick="showTab('midwife')" style="background: linear-gradient(135deg, #E91E63, #9C27B0); color: white;">🤰 ডিজিটাল মিডওয়াইফ</button>
        </div>'''

new_tabs = '''        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('midwife')" style="background: linear-gradient(135deg, #E91E63, #9C27B0); color: white;">🤰 ডিজিটাল মিডওয়াইফ</button>
            <button class="tab-btn" onclick="showTab('food')">🍎 খাদ্য বিশ্লেষণ</button>
        </div>'''

content = content.replace(old_tabs, new_tabs)
print("✅ Updated tab buttons")

# 2. Remove voice-tab content (from <!-- Voice Chat Tab --> to <!-- Prescription Tab -->)
voice_start = content.find('<!-- Voice Chat Tab -->')
prescription_start = content.find('<!-- Prescription Tab -->')

if voice_start != -1 and prescription_start != -1:
    content = content[:voice_start] + content[prescription_start:]
    print("✅ Removed voice-tab content")

# 3. Remove prescription-tab content (from <!-- Prescription Tab --> to <!-- Food Analysis Tab)
prescription_start = content.find('<!-- Prescription Tab -->')
food_start = content.find('<!-- Food Analysis Tab')

if prescription_start != -1 and food_start != -1:
    content = content[:prescription_start] + content[food_start:]
    print("✅ Removed prescription-tab content")

# 4. Update food-tab to not be active by default (midwife is now active)
# And update midwife-tab to be active
content = content.replace('id="food-tab" class="tab-content active"', 'id="food-tab" class="tab-content"')
content = content.replace('id="midwife-tab" class="tab-content"', 'id="midwife-tab" class="tab-content active"')
print("✅ Set midwife tab as active")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Done! Voice Chat and Prescription tabs removed.")
print("Digital Midwife is now the default tab.")
