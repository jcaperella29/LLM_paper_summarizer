# 🧠 JCAP AI Paper Summarizer  

A Flask-based AI-powered web application that extracts text from **scientific PDFs**, generates **summaries** using **Ollama**, and **extracts figures** (plots & images) from research papers. It supports **batch processing** via ZIP file uploads and allows users to **download individual summaries** as PDFs.


---

## 🚀 Features  

✅ **Multi-PDF Summarization** - Upload multiple PDFs in a ZIP file and get separate summaries for each paper.  
✅ **Figure Extraction** - Automatically detects and extracts figures (plots) from research papers.  
✅ **Dynamic UI** - Each PDF gets its **own tab** for summaries & figures.  
✅ **Downloadable Summaries** - Saves each summary as a **PDF** for easy access.  
✅ **Batch Processing** - Handles multiple PDFs in one go.  

---

## 📸 Screenshots  

### 📝 Summarization Output  
![Summary Screenshot](static/screenshots/summary_screenshot.png)  

### 📊 Extracted Figures  
![Figures Screenshot](static/screenshots/figures_screenshot.png)  

---

## 📦 Installation  

### 1️⃣ Clone the Repository  
```sh
git clone https://github.com/YOUR_USERNAME/JCAP_AI_PAPER_SUMMARIZER.git
cd JCAP_AI_PAPER_SUMMARIZER
2️⃣ Install Dependencies
Ensure you have Python 3.10+ and run:

sh
Copy
Edit
pip install -r requirements.txt
3️⃣ Start the Flask App
sh
Copy
Edit
python app.py
The app will be available at:
👉 http://127.0.0.1:5000/

🖥️ Usage
Step 1 - Upload PDFs
You can upload individual PDFs or batch process multiple PDFs in a ZIP file.
Click Upload and the app will begin extracting & summarizing content.
Step 2 - View Summaries
Each PDF gets its own summary tab dynamically labeled based on the file name.
You can download individual summaries as PDFs.
Step 3 - View Extracted Figures
The app extracts plots/figures from the PDFs and displays them under the Figures tab.
