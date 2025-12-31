
import os
from fpdf import FPDF

def markdown_to_pdf(md_path, pdf_path):
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found.")
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Use standard DejaVu or similar if available, but standard fonts are safer for a quick script
    # Standard Helvetica/Arial
    pdf.set_font("Helvetica", size=12)

    for line in lines:
        line = line.strip('\n')
        
        # Heading 1
        if line.startswith("# "):
            pdf.ln(10)
            pdf.set_font("Helvetica", style="B", size=20)
            pdf.multi_cell(0, 10, line[2:])
            pdf.set_font("Helvetica", size=12)
            pdf.ln(5)
            
        # Heading 2
        elif line.startswith("## "):
            pdf.ln(8)
            pdf.set_font("Helvetica", style="B", size=16)
            pdf.multi_cell(0, 10, line[3:])
            pdf.set_font("Helvetica", size=12)
            pdf.ln(4)
            
        # Heading 3
        elif line.startswith("### "):
            pdf.ln(6)
            pdf.set_font("Helvetica", style="B", size=14)
            pdf.multi_cell(0, 10, line[4:])
            pdf.set_font("Helvetica", size=12)
            pdf.ln(2)
            
        # Lists
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            pdf.set_font("Helvetica", size=12)
            # Basic indentation for lists
            pdf.multi_cell(0, 7, "  " + chr(149) + " " + line.strip()[2:])
            
        # Tables (Very basic handling - just print as text for now or skip to keep it clean)
        elif "|" in line and "---" not in line:
            pdf.set_font("Courier", size=10)
            pdf.multi_cell(0, 6, line)
            pdf.set_font("Helvetica", size=12)
            
        # Normal lines
        elif line.strip():
            # Bold/Italic markers
            pdf.set_font("Helvetica", size=12)
            clean_line = line.replace("**", "").replace("__", "").replace("`", "")
            pdf.multi_cell(0, 7, clean_line)
            
        # Empty lines
        else:
            pdf.ln(2)

    pdf.output(pdf_path)
    print(f"Successfully generated PDF: {pdf_path}")

if __name__ == "__main__":
    artifact_dir = r"c:\Users\User\.gemini\antigravity\brain\afba1105-af9d-43ec-9c25-6505ceb804ec"
    md_file = os.path.join(artifact_dir, "technical_documentation.md")
    pdf_file = os.path.join(artifact_dir, "Janani_AI_Technical_Documentation.pdf")
    
    markdown_to_pdf(md_file, pdf_file)
