# -*- coding: utf-8 -*-
# Fix Bengali text by byte-level replacement

with open('templates/index.html', 'rb') as f:
    data = f.read()

# Direct byte replacements - mojibake bytes -> correct UTF-8 bytes
byte_replacements = [
    # 🎤 ভয়েস চ্যাট (Voice Chat)
    (b'\xc3\xb0\xc5\xb8\xc5\xbd\xc2\xa4 \xc3\xa0\xc2\xa6\xc2\xad\xc3\xa0\xc2\xa6\xc2\xaf\xc3\xa0\xc2\xa6\xc2\xbc\xc3\xa0\xc2\xa7\xe2\x80\xa1\xc3\xa0\xc2\xa6\xc2\xb8 \xc3\xa0\xc2\xa6\xc5\xa1\xc3\xa0\xc2\xa7\xc2\x8d\xc3\xa0\xc2\xa6\xc2\xaf\xc3\xa0\xc2\xa6\xc2\xbe\xc3\xa0\xc2\xa6\xc5\xb8',
     '\U0001F3A4 ভয়েস চ্যাট'.encode('utf-8')),
    
    # 💊 প্রেসক্রিপশন (Prescription) - find pattern first
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x99\xc5\xa0', '\U0001F48A'.encode('utf-8')),
    
    # 🎈 খাদ্য বিশ্লেষণ (Food Analysis)
    (b'\xc3\xb0\xc5\xb8\xc5\xbd\xc2\x88', '\U0001F388'.encode('utf-8')),
]

# Try a different approach - just decode properly
# The text is UTF-8 that was misread as Windows-1252 then saved as UTF-8
# We need to undo this

try:
    # First decode as UTF-8
    text = data.decode('utf-8')
    
    # Check if it has mojibake markers
    if '\xc3\xb0' in text or 'Ã°' in text:
        print("Detected double-encoding, attempting fix...")
        # Encode as raw bytes using latin-1, then decode as UTF-8
        # This reverses the double-encoding
        fixed = text.encode('raw_unicode_escape').decode('unicode_escape')
        # If that doesn't work, try windows-1252
        if 'à¦' in fixed:
            fixed = text.encode('windows-1252', errors='surrogateescape').decode('utf-8', errors='replace')
        text = fixed
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    
    print("File saved!")
    
    # Check result
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        check = f.read()
    
    if 'ভয়েস' in check or 'চ্যাট' in check:
        print("✅ Bengali text is now correct!")
    else:
        # Show what we have
        idx = check.find('showTab')
        if idx > 0:
            print("Sample around showTab:", repr(check[idx:idx+100]))
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
