# Fix duplicate AR Labor code that appears outside script tags

html_file = 'templates/index.html'

with open(html_file, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Find and remove the duplicate code that starts after </script>
# Pattern: </script>// ============ AR LABOR ASSISTANT FUNCTIONS ============ ... </script>

# Find the problematic section
bad_start = '    </script>// ============ AR LABOR ASSISTANT FUNCTIONS ============'
bad_end_marker = "setTimeout(initARLaborAssistant, 1000);\n        });\n        \n\n    </script>"

if bad_start in content:
    start_idx = content.find(bad_start)
    # Find the ending </script> after this bad section
    end_idx = content.find(bad_end_marker, start_idx)
    
    if end_idx != -1:
        end_idx = end_idx + len(bad_end_marker)
        # Replace the bad section with just proper closing
        content = content[:start_idx] + '    </script>' + content[end_idx:]
        print("✅ Removed duplicate AR Labor code from outside script tags")
    else:
        print("❌ Could not find end marker")
else:
    print("ℹ️ No duplicate found or already fixed")

# Write back
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fix complete!")
