function showTab(tabId) {
    console.log("Switching to tab:", tabId);

    document.getElementById('upload-tab').style.display = 'none';
    document.getElementById('summary-tab').style.display = 'none';
    document.getElementById('figures-tab').style.display = 'none';

    document.getElementById(tabId).style.display = 'block';
}

function uploadFile() {
    console.log("Upload button clicked");

    let formData = new FormData(document.getElementById('upload-form'));
    document.getElementById('progress-container').style.display = 'block';
    document.getElementById('progress-bar').style.width = '0%';
    document.getElementById('summary-text').innerText = '';
    document.getElementById('figures-container').innerHTML = '';  

    fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("✅ Response received:", data);

        document.getElementById('progress-bar').style.width = '100%';
        setTimeout(() => showTab('summary-tab'), 500);

        if (data.summary && data.summary.trim() !== "Error: No summary generated.") {
            document.getElementById('summary-text').innerText = data.summary;
        } else {
            document.getElementById('summary-text').innerText = "❌ Summary not available.";
        }

        document.getElementById('download-button').style.display = 'block';
        document.getElementById('download-button').setAttribute("href", data.pdf_url);

        if (data.figures.length > 0) {
            console.log("✅ Figures found, updating UI...");
            document.getElementById("figures-tab-btn").style.display = "inline-block";  
            document.getElementById("figures-container").innerHTML = "";  

            data.figures.forEach(function(figureUrl) {
                let imgElement = document.createElement("img");
                imgElement.src = figureUrl;
                imgElement.style.maxWidth = "100%";
                imgElement.alt = "Extracted figure";
                document.getElementById("figures-container").appendChild(imgElement);
            });

            setTimeout(() => showTab('figures-tab'), 1000);
        } else {
            console.log("❌ No figures found in response.");
            document.getElementById("figures-container").innerText = "❌ No figures found.";
        }
    })
    .catch(error => console.error('❌ Error:', error));
}
