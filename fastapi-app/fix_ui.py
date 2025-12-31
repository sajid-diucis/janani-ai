# Direct text replacement script using regex
import re

with open('templates/index.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Replace the entire tabs div section with correct Bengali
old_tabs_pattern = r'<div class="tabs">.*?</div>\s*\n\s*<!-- Voice Chat Tab'
new_tabs = '''<div class="tabs">
            <button class="tab-btn active" onclick="showTab('voice')">🎤 ভয়েস চ্যাট</button>
            <button class="tab-btn" onclick="showTab('prescription')">💊 প্রেসক্রিপশন</button>
            <button class="tab-btn" onclick="showTab('food')">🍎 খাদ্য বিশ্লেষণ</button>
            <button class="tab-btn" onclick="showTab('midwife')" style="background: linear-gradient(135deg, #E91E63, #9C27B0); color: white;">🤰 ডিজিটাল মিডওয়াইফ</button>
        </div>
        
        <!-- Voice Chat Tab'''

content = re.sub(old_tabs_pattern, new_tabs, content, flags=re.DOTALL)

# Replace header
old_header_pattern = r'<h1[^>]*>.*?</h1>\s*<p[^>]*>.*?</p>'
new_header = '''<h1 style="font-size: 2.5em; margin-bottom: 10px;">🤰 জননী AI</h1>
                <p style="font-size: 1.1em; opacity: 0.9;">বাংলায় মাতৃস্বাস্থ্য সহায়ক | Bengali Maternal Health Assistant</p>'''

content = re.sub(old_header_pattern, new_header, content, count=1, flags=re.DOTALL)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed tabs and header!")

# Verify
with open('templates/index.html', 'r', encoding='utf-8') as f:
    check = f.read()

if 'ভয়েস চ্যাট' in check:
    print("✅ Tab buttons are correct!")
if 'জননী AI' in check:
    print("✅ Header is correct!")
