import markdown
import os

MARKDOWN_FILE = r"C:\Users\User\.gemini\antigravity\brain\b25fceb4-d471-4765-8499-a417be8a439d\replication_guide.md"
HTML_FILE = r"c:\Users\User\Documents\buildathon\Janani\fastapi-app\replication_guide.html"

css = """
<style>
    body { font-family: sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
    pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
    blockquote { border-left: 5px solid #ccc; margin: 0; padding-left: 10px; color: #555; }
    h1, h2, h3 { color: #333; }
    code { background: #eee; padding: 2px 5px; border-radius: 3px; }
</style>
"""

with open(MARKDOWN_FILE, "r", encoding="utf-8") as f:
    text = f.read()

html = markdown.markdown(text)
full_html = f"<html><head>{css}</head><body>{html}</body></html>"

with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(full_html)
    
print(f"Generated HTML at: {HTML_FILE}")
