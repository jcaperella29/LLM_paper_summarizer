import fitz  # PyMuPDF for PDF processing
import os
import zipfile
import requests
from flask import Flask, request, render_template, jsonify, send_file, send_from_directory
from fpdf import FPDF

app = Flask(__name__, static_folder="static")

UPLOAD_FOLDER = "uploads"
SUMMARY_FOLDER = "summaries"
FIGURE_FOLDER = "static/figures"

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SUMMARY_FOLDER, exist_ok=True)
os.makedirs(FIGURE_FOLDER, exist_ok=True)

OLLAMA_URL = "https://ollama-service-hidden-waterfall-2124.fly.dev/api/generate"

### 📌 Function to Summarize Text ###
def summarize_text(text, chunk_size=3000):
    """
    Sends extracted text to Ollama for summarization.
    Processes text in **chunks** to avoid timeouts.
    """
    text_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    summaries = []

    for idx, chunk in enumerate(text_chunks):
        print(f"📌 Processing chunk {idx + 1}/{len(text_chunks)}")  # Debugging log
        try:
            response = requests.post(
                OLLAMA_URL,
                json={"model": "mistral", "prompt": f"Summarize this:\n{chunk}", "stream": False},
                timeout=120
            )
            response_json = response.json()
            summary = response_json.get("response", "Error: No response from Ollama.")
            summaries.append(summary)
        except requests.exceptions.Timeout:
            print(f"❌ Error: Ollama request timed out on chunk {idx + 1}")
            summaries.append("Error: Timeout on this chunk.")

    return "\n\n".join(summaries)  # Combine summaries

### 📌 Function to Extract Text from PDF ###
def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF and returns it as a single string.
    """
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])
    return text.strip()

### 📌 Function to Generate Summary PDF ###
def create_summary_pdf(summary_text, pdf_filename):
    """
    Saves a given summary text into a **downloadable** PDF file.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Summary", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary_text)
    pdf.output(pdf_filename)

### 📌 Flask Routes ###
@app.route("/")
def index():
    return render_template("index.html")

# Serve static files (CSS, JS)
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Handles uploaded PDF files, extracts text, summarizes it, and saves results.
    """
    print("✅ Received upload request")  # Debugging print

    if "file" not in request.files:
        print("❌ Error: No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        print("❌ Error: No selected file")
        return jsonify({"error": "No selected file"}), 400

    # Save file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    print(f"✅ File saved at {filepath}")

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(filepath)
    if not extracted_text:
        return jsonify({"error": "Could not extract text from PDF."}), 400

    # Summarize the extracted text
    summary_text = summarize_text(extracted_text)

    # Save summary as PDF
    pdf_name = file.filename.replace(".pdf", "_summary.pdf")
    pdf_summary_path = os.path.join(SUMMARY_FOLDER, pdf_name)
    create_summary_pdf(summary_text, pdf_summary_path)

    print("✅ Summary generated successfully")

    return jsonify({
        "message": "File processed successfully",
        "summary": summary_text,
        "download_link": f"/download_summary/{pdf_name}"
    })

# API Endpoint: Download Summaries
@app.route("/download_summary/<pdf_name>")
def download_summary(pdf_name):
    """
    Allows users to download **individual** summary PDFs.
    """
    pdf_path = os.path.join(SUMMARY_FOLDER, pdf_name)
    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Use the correct Fly.io port
    app.run(host="0.0.0.0", port=port)  # Listen on all interfaces
