 document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ JCAP_AI_PAPER_SUMMARIZER loaded successfully!");
    console.log("📌 Checking button and input elements...");
    
    let uploadButton = document.getElementById("uploadButton");
    let fileInput = document.getElementById("fileInput");

    console.log("Upload Button:", uploadButton);
    console.log("File Input:", fileInput);

    if (!fileInput) {
        console.error("❌ Error: File input element not found in DOM!");
    }

    if (uploadButton) {
        uploadButton.addEventListener("click", function(event) {
            event.preventDefault(); // Prevent default form submission
            uploadFile();
        });
    } else {
        console.error("❌ Upload button not found! Check index.html.");
    }
});

// Function to handle tab switching
function showTab(tabId) {
    document.querySelectorAll('.tab').forEach(tab => tab.style.display = 'none');
    let selectedTab = document.getElementById(tabId);

    if (selectedTab) {
        selectedTab.style.display = 'block';
        console.log(`🔄 Switching to tab: ${tabId}`);
    } else {
        console.error(`❌ Tab not found: ${tabId}`);
    }
}

// Function to handle file upload
function uploadFile() {
    console.log("📌 Upload button clicked");

    let fileInput = document.getElementById("fileInput");

    if (!fileInput || fileInput.files.length === 0) {
        console.error("❌ No file selected!");
        alert("Please select a file before uploading.");
        return;
    }

    let formData = new FormData(document.getElementById("upload-form"));

    document.getElementById("progress-container").style.display = "block";
    document.getElementById("progress-bar").style.width = "0%";

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
                img.src = fig.startsWith("http") ? fig : "/static/figures/" + fig;
                img.alt = "Extracted Figure";
                figuresContent.appendChild(img);
            });

            figuresTab.appendChild(figuresContent);
        });

        showTab("summary-tab");
    })
    .catch(error => console.error("❌ Fetch error:", error));
}

// Expose function to global scope
window.uploadFile = uploadFile;

