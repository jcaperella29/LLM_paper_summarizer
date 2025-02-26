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

### 📌 Function to Summarize Text with Chunk Processing ###
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
                "http://localhost:11434/api/generate",
                json={"model": "mistral", "prompt": f"Summarize this:\n{chunk}", "stream": False},
                timeout=120
            )
            summary = response.json().get("response", "Error: No response from Ollama.")
            summaries.append(summary)
        except requests.exceptions.Timeout:
            print(f"❌ Error: Ollama request timed out on chunk {idx + 1}")
            summaries.append("Error: Timeout on this chunk.")

    return "\n\n".join(summaries)  # Combine summaries

### 📌 Function to Extract Text from PDF (Supports Chunking) ###
def extract_text_from_pdf(pdf_path, chunk_size=3000):
    """
    Extracts text from a PDF and returns it in **manageable chunks**.
    """
    doc = fitz.open(pdf_path)
    text_chunks = []
    current_text = ""

    for page in doc:
        current_text += page.get_text("text") + "\n"
        if len(current_text) >= chunk_size:
            text_chunks.append(current_text)
            current_text = ""

    if current_text:
        text_chunks.append(current_text)

    return " ".join(text_chunks)  # Return full extracted text

### 📌 Function to Extract Figures (Images) from a PDF ###
def extract_figures_from_pdf(pdf_path, output_folder):
    """
    Extracts images from a PDF file and saves them in a specified folder.
    """
    doc = fitz.open(pdf_path)
    extracted_images = []
    pdf_filename = os.path.basename(pdf_path).replace(".pdf", "")

    for i, page in enumerate(doc):
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            img_data = doc.extract_image(xref)
            img_bytes = img_data["image"]
            img_ext = img_data["ext"]

            img_filename = f"{pdf_filename}_page{i+1}_img{img_index+1}.{img_ext}"
            img_path = os.path.join(output_folder, img_filename)

            with open(img_path, "wb") as f:
                f.write(img_bytes)

            extracted_images.append(img_filename)

    return extracted_images  # List of extracted image filenames

### 📌 Function to Process ZIP Files (Extract PDFs) ###
def process_zip(zip_path):
    """
    Extracts PDFs from a ZIP file and processes them.
    """
    extracted_files = []
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(UPLOAD_FOLDER)
        extracted_files = [os.path.join(UPLOAD_FOLDER, f) for f in zip_ref.namelist() if f.endswith(".pdf")]
    return extracted_files

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
    Handles uploaded ZIP or PDF files, extracts data, summarizes text, and extracts figures.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    print(f"✅ File saved at {filepath}")

    pdf_files = []

    # Handle ZIP Files
    if file.filename.endswith(".zip"):
        pdf_files = process_zip(filepath)
        print(f"📌 Extracted {len(pdf_files)} PDFs from ZIP.")
    else:
        pdf_files.append(filepath)  # Single PDF case

    if not pdf_files:
        return jsonify({"error": "No PDFs found."}), 400

    response_data = {"summaries": {}, "figures": {}, "download_links": {}}

    for pdf in pdf_files:
        pdf_name = os.path.basename(pdf).replace(".pdf", "")
        extracted_text = extract_text_from_pdf(pdf)
        summary_text = summarize_text(extracted_text) if extracted_text else "Error: No summary generated."
        response_data["summaries"][pdf_name] = summary_text

        figures = extract_figures_from_pdf(pdf, FIGURE_FOLDER)
        response_data["figures"][pdf_name] = figures

        # Save summary PDF
        pdf_summary_path = os.path.join(SUMMARY_FOLDER, f"{pdf_name}_summary.pdf")
        create_summary_pdf(summary_text, pdf_summary_path)

        # ✅ Only add a single correct download link (Fixes extra button issue)
        response_data["download_links"][pdf_name] = f"/download_summary/{pdf_name}"

    print(f"📌 Sending response: {response_data}")
    return jsonify(response_data)

# API Endpoint: Download Summaries
@app.route("/download_summary/<pdf_name>")
def download_summary(pdf_name):
    """
    Allows users to download **individual** summary PDFs.
    """
    pdf_path = os.path.join(SUMMARY_FOLDER, f"{pdf_name}_summary.pdf")
    return send_file(pdf_path, as_attachment=True)

# API Endpoint: Serve Extracted Figures
@app.route("/static/figures/<filename>")
def serve_figure(filename):
    """
    Allows users to view/download extracted figures.
    """
    return send_from_directory(FIGURE_FOLDER, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Fix: Use Cloud Run's port 8080
    app.run(host="0.0.0.0", port=port)        # Fix: Listen on all interface
