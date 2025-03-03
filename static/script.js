
            `;
          document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ JCAP_AI_PAPER_SUMMARIZER loaded successfully!");
    console.log("📌 Checking button and input elements...");
   console.log("Upload Button:", document.getElementById('uploadButton'));
    console.log("File Input:", document.getElementById('fileInput'));

    let uploadButton = document.getElementById('uploadButton'); // ✅ Fixed ID

    if (uploadButton) {
        uploadButton.addEventListener("click", uploadFile);
    } else {
        console.error("❌ Upload button not found! Check index.html.");
    }
});

// Function to handle tab switching
function showTab(tabId) {
    document.querySelectorAll('.tab').forEach(tab => tab.style.display = 'none');
    document.getElementById(tabId).style.display = 'block';
    console.log(`🔄 Switching to tab: ${tabId}`);
}

function uploadFile() {
    console.log("📌 Upload button clicked");

    let formData = new FormData(document.getElementById('upload-form'));

    document.getElementById('progress-container').style.display = 'block';
    document.getElementById('progress-bar').style.width = '0%';

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("✅ Full response:", data);

        let summaryTab = document.getElementById("summary-tab");
        let figuresTab = document.getElementById("figures-tab");
        summaryTab.innerHTML = "<h2>Summaries</h2>";
        figuresTab.innerHTML = "<h2>Figures</h2>";

        // ✅ Safety check for missing summaries
        if (!data.summaries || typeof data.summaries !== "object") {
            console.error("❌ Error: Summaries are missing in response!");
            return;
        }

        if (!data.figures || typeof data.figures !== "object") {
            console.error("❌ Error: Figures are missing in response!");
            return;
        }

        // Populate summaries
        Object.keys(data.summaries).forEach(pdfName => {
            let summaryContent = document.createElement("div");
            summaryContent.innerHTML = `
                <h3>${pdfName} Summary</h3>
                <p>${data.summaries[pdfName]}</p>
                <a href="${data.download_links[pdfName]}" download>
                    <button>Download Summary</button>
                </a>
            `;
            summaryTab.appendChild(summaryContent);
        });

        // Populate figures
        Object.keys(data.figures).forEach(pdfName => {
            let figuresContent = document.createElement("div");
            figuresContent.innerHTML = `<h3>${pdfName} Figures</h3>`;

            data.figures[pdfName].forEach(fig => {
                let img = document.createElement("img");
                img.src = fig.startsWith("http") ? fig : "/static/figures/" + fig; // ✅ Fixed path issue
                img.alt = "Extracted Figure";
                figuresContent.appendChild(img);
            });

            figuresTab.appendChild(figuresContent);
        });

        showTab('summary-tab');
    })
    .catch(error => console.error("❌ Fetch error:", error));
}
