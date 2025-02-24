import fitz  # PyMuPDF for PDF processing

from flask import Flask, request, render_template, jsonify, send_file
import os
from fpdf import FPDF

import requests
import io
from PIL import Image
import fitz  # PyMuPDF
import io
from PIL import Image
import os

def extract_figures_from_pdf(pdf_path):
    """
    Extracts both raster images and vector figures from a PDF.
    Saves them as separate images in /static/figures.
    """
    output_folder = "static/figures"
    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(pdf_path)
    figure_paths = []
    img_count = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images(full=True)

        # Extract raster images (PNG, JPEG)
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            img_ext = base_image["ext"]

            # Save the extracted image
            img_filename = f"figure_{page_num+1}_{img_index+1}.{img_ext}"
            img_path = os.path.join(output_folder, img_filename)

            with open(img_path, "wb") as f:
                f.write(image_bytes)

            figure_paths.append(f"/static/figures/{img_filename}")
            img_count += 1

        # Extract vector figures (Cropping detected bounding boxes)
        for rect in page.get_drawings():
            x0, y0, x1, y1 = rect["rect"]  # Bounding box
            width = x1 - x0
            height = y1 - y0

            # Ignore small lines and elements
            if width > 100 and height > 100:
                pix = page.get_pixmap(clip=(x0, y0, x1, y1), matrix=fitz.Matrix(2, 2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                img_filename = f"vector_figure_{page_num+1}_{img_count+1}.png"
                img_path = os.path.join(output_folder, img_filename)
                img.save(img_path, "PNG")

                figure_paths.append(f"/static/figures/{img_filename}")
                img_count += 1

    print(f"📌 Extracted {img_count} figures.")
    return figure_paths

def summarize_text(text, chunk_size=1000):
    """
    Summarizes large text in smaller chunks to prevent Ollama timeouts.
    Ensures that the function still returns a valid summary even if some chunks fail.
    """
    prompt_template = "Summarize this scientific paper:\n\n"
    text_chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    
    full_summary = ""
    for idx, chunk in enumerate(text_chunks):
        print(f"Processing chunk {idx + 1}/{len(text_chunks)}")  # Debug log
        
        prompt = prompt_template + chunk
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "mistral", "prompt": prompt, "stream": False},
                timeout=180  # Increased timeout for reliability
            )
            print(f"Ollama response received for chunk {idx + 1}")  # Debugging log
            full_summary += response.json().get("response", "") + "\n"

        except requests.exceptions.Timeout:
            print(f"Error: Ollama request timed out on chunk {idx + 1}")
            full_summary += f"\n[Error: Ollama timed out on chunk {idx + 1}]\n"

    return full_summary.strip() if full_summary.strip() else "Error: No summary generated."


def extract_text_from_pdf(pdf_path, chunk_size=3000):
    """
    Extracts text from a PDF and chunks it for easier processing.
    """
    doc = fitz.open(pdf_path)
    text_chunks = []
    current_text = ""

    for page in doc:
        current_text += page.get_text("text") + "\n"
        if len(current_text) >= chunk_size:
            text_chunks.append(current_text.strip())
            current_text = ""

    if current_text:
        text_chunks.append(current_text.strip())

    return " ".join(text_chunks)


app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
SUMMARY_FOLDER = "summaries"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SUMMARY_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    print(f"File saved at {filepath}")

    # Extract text and figures
    extracted_text = extract_text_from_pdf(filepath)
    figures = extract_figures_from_pdf(filepath)  # NEW - Proper figure extraction
    summary_text = summarize_text(extracted_text)

    # Save summary as PDF
    pdf_filename = os.path.join(SUMMARY_FOLDER, "summary.pdf")
    create_summary_pdf(summary_text, pdf_filename)

    return jsonify({
        "summary": summary_text,
        "pdf_url": "/download_summary",
        "figures": figures  # Send figure paths
    })

@app.route("/download_summary")
def download_summary():
    pdf_path = os.path.join(SUMMARY_FOLDER, "summary.pdf")
    return send_file(pdf_path, as_attachment=True)

def create_summary_pdf(summary_text, pdf_filename):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Summary", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary_text)
    pdf.output(pdf_filename)

if __name__ == "__main__":
    app.run(debug=True)
