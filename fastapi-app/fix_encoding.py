# Fix encoding issues in index.html
import codecs

# Read the file as bytes
with open('templates/index.html', 'rb') as f:
    content = f.read()

# Try to decode as UTF-8, if that fails try latin-1 then re-encode
try:
    # The file seems to be double-encoded or saved with wrong encoding
    # First decode as latin-1 (which will read any byte), then fix the UTF-8 sequences
    text = content.decode('utf-8')
    
    # Check if we have mojibake (incorrectly decoded UTF-8)
    # Common pattern: Bengali text showing as Ã¦, Ã§, etc.
    if 'Ã¦' in text or 'à¦' in text or 'ðŸ' in text:
        print("Detected mojibake, attempting to fix...")
        # The file was likely saved as UTF-8, read as latin-1, saved again
        # We need to encode back to latin-1 then decode as UTF-8
        try:
            fixed_text = text.encode('latin-1').decode('utf-8')
            text = fixed_text
            print("Fixed encoding successfully!")
        except:
            print("Could not fix with latin-1 -> utf-8 conversion")
    
    # Write back with proper UTF-8 encoding
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    
    print("File saved with UTF-8 encoding")
    
    # Verify by reading back
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        verify = f.read()
        if 'জননী' in verify or 'ভয়েস' in verify:
            print("✅ Bengali text is now correct!")
        else:
            print("⚠️ Bengali text may still have issues")
            # Show a sample
            idx = verify.find('tab-btn')
            if idx != -1:
                print("Sample:", verify[idx:idx+100])

except Exception as e:
    print(f"Error: {e}")
