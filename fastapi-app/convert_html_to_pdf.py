from xhtml2pdf import pisa
import os

HTML_FILE = r"c:\Users\User\Documents\buildathon\Janani\fastapi-app\replication_guide.html"
PDF_FILE = r"c:\Users\User\Documents\buildathon\Janani\fastapi-app\replication_guide.pdf"

def convert_html_to_pdf(source_html, output_filename):
    # Open file to read HTML
    with open(source_html, "r", encoding="utf-8") as f:
        source_html_content = f.read()

    # Open file to write PDF
    with open(output_filename, "wb") as result_file:
        # Convert HTML to PDF
        div_rules = """
        <style>
            @page { size: A4; margin: 1cm; }
            body { font-family: Helvetica, sans-serif; font-size: 10pt; }
            h1 { font-size: 16pt; color: #333; }
            h2 { font-size: 14pt; color: #555; margin-top: 15px; }
            h3 { font-size: 12pt; color: #666; }
            pre { background-color: #f0f0f0; padding: 10px; font-family: Courier; font-size: 8pt; white-space: pre-wrap; }
            blockquote { border-left: 2px solid #ccc; padding-left: 10px; color: #555; }
        </style>
        """
        # Inject style into the HTML content for PDF
        source_html_content = source_html_content.replace("<head>", f"<head>{div_rules}")
        
        pisa_status = pisa.CreatePDF(
            source_html_content,                # the HTML to convert
            dest=result_file                    # file handle to recieve result
        )

    return pisa_status.err

if __name__ == "__main__":
    print(f"Converting {HTML_FILE} to {PDF_FILE}...")
    error = convert_html_to_pdf(HTML_FILE, PDF_FILE)
    if not error:
        print(f"SUCCESS: Created {PDF_FILE}")
    else:
        print(f"ERROR: PDF generation failed.")
