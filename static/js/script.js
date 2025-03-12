document.addEventListener("DOMContentLoaded", function () {
  // Retrieve and display stored data on page load
  const storedSummary = localStorage.getItem("pdfSummary");
  if (storedSummary) {
    document.getElementById("summary").innerText = storedSummary;
  }

  const storedResponse = localStorage.getItem("pdfResponse");
  if (storedResponse) {
    document.getElementById("response").innerText = storedResponse;
  }

  const storedOrgInfo = localStorage.getItem("orgInfo");
  if (storedOrgInfo) {
    document.getElementById("orgInfo").innerText = storedOrgInfo;
  }

  const storedImages = localStorage.getItem("extractedImages");
  if (storedImages) {
    displayImagesAndDescriptions(JSON.parse(storedImages));
  }
});

function logoutUser() {
  localStorage.clear(); // Clear all stored data
  sessionStorage.clear(); // Clear session storage if needed
  window.location.href = "{{ url_for('logout') }}"; // Redirect to logout
}

function showFileName() {
  const fileInput = document.getElementById("pdf_file");
  const fileName = fileInput.files[0] ? fileInput.files[0].name : "";
  document.getElementById("fileName").innerText = fileName
    ? `Selected File: ${fileName}`
    : "";
}

function toggleLoading(show) {
  document.getElementById("spinnerContainer").style.display = show
    ? "flex"
    : "none";
  document.body.classList.toggle("blur", show); // Add or remove blur effect
}

function submitPdf() {
  const fileInput = document.getElementById("pdf_file");

  // Validate if a file is selected
  if (!fileInput.files.length) {
    alert("Please select a PDF file to upload.");
    return;
  }

  toggleLoading(true); // Show spinner and apply blur

  const formData = new FormData();
  formData.append("pdf_file", fileInput.files[0]);

  fetch("/process_pdf", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      showAlert("PDF Processed successfully");
    })
    .catch((error) => {
      document.getElementById("summary").innerText = "Error: " + error;
    })
    .finally(() => {
      toggleLoading(false); // Hide spinner and remove blur
    });
}

function summarizePdf(type) {
  const fileInput = document.getElementById("pdf_file");

  if (!fileInput.files.length) {
    alert("Please select a PDF file to summarize.");
    return;
  }

  toggleLoading(true); // Show spinner and apply blur

  const formData = new FormData();
  formData.append("pdf_file", fileInput.files[0]);
  formData.append("summary_type", type);

  fetch("/summarize_pdf", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      const summary = data.summary || data.error;
      document.getElementById("summary").innerText = summary;
      localStorage.setItem("pdfSummary", summary); // Store summary in localStorage
    })
    .catch((error) => {
      document.getElementById("summary").innerText = "Error: " + error;
    })
    .finally(() => {
      toggleLoading(false); // Hide spinner and remove blur
    });
}

function askQuestion() {
  const question = document.getElementById("question").value;

  if (!question) {
    alert("Please enter a question.");
    return;
  }

  toggleLoading(true); // Show spinner and apply blur

  fetch("/ask_question", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  })
    .then((response) => response.json())
    .then((data) => {
      const response = data.response || data.error;
      document.getElementById("response").innerText = response;
      localStorage.setItem("pdfResponse", response); // Store response in localStorage
    })
    .catch((error) => {
      document.getElementById("response").innerText = "Error: " + error;
    })
    .finally(() => {
      toggleLoading(false); // Hide spinner and remove blur
    });
}

function fetchOrgInfo() {
  const fileInput = document.getElementById('pdf_file');

  if (fileInput.files.length === 0) {
    alert("Please upload a PDF file first.");
    return;
  }

  const formData = new FormData();
  formData.append('pdf_file', fileInput.files[0]);

  toggleLoading(true); // Show spinner and apply blur

  fetch('/fetch_org_info', {
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert(data.error);
      } else {
        const orgInfo = data.orgInfo;
        document.getElementById('orgInfo').innerText = orgInfo;
        localStorage.setItem("orgInfo", orgInfo); // Store org info in localStorage
      }
    })
    .catch(error => {
      console.error('Error:', error);
      document.getElementById('orgInfo').innerText = "Error: " + error;
    })
    .finally(() => {
      toggleLoading(false); // Hide spinner and remove blur
    });
}

function extractImages() {
  const fileInput = document.getElementById("pdf_file");

  if (!fileInput.files.length) {
    alert("Please select a PDF file to extract images.");
    return;
  }

  toggleLoading(true); // Show spinner and apply blur

  const formData = new FormData();
  formData.append("pdf_file", fileInput.files[0]);

  // Step 1: Extract images
  fetch("/extract_images", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        throw new Error(data.error);
      }
      showAlert("Images extracted successfully");

      // Step 2: Analyze the extracted images
      return fetch("/analyze_images", {
        method: "POST",
        body: formData,
      });
    })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        throw new Error(data.error);
      }
      // Display images and their descriptions
      displayImagesAndDescriptions(data.images);
      localStorage.setItem("extractedImages", JSON.stringify(data.images)); // Store images in localStorage
    })
    .catch((error) => {
      showAlert("Error: " + error.message);
    })
    .finally(() => {
      toggleLoading(false); // Hide spinner and remove blur
    });
}

function displayImagesAndDescriptions(images) {
  const imageContainer = document.getElementById("imageContainer");
  imageContainer.innerHTML = ""; // Clear previous content

  if (!images || images.length === 0) {
    imageContainer.innerHTML = "<p>No images found in the PDF.</p>";
    return;
  }

  images.forEach((image) => {
    const imageElement = document.createElement("div");
    imageElement.className = "image-item";

    // Display the image
    const img = document.createElement("img");
    img.src = image.url; // Use the URL returned by the backend
    img.alt = "Extracted Image";
    imageElement.appendChild(img);

    // Convert Markdown description to HTML
    const descriptionHTML = marked.parse(image.description);

    // Display the generated description as HTML
    const description = document.createElement("div");
    description.innerHTML = descriptionHTML; // Use innerHTML to render the HTML
    description.className = "description-content"; // Add a class for styling
    imageElement.appendChild(description);

    imageContainer.appendChild(imageElement);
  });
}

function showAlert(message) {
  const alertElement = document.getElementById("alertMessage");
  alertElement.innerText = message;
  alertElement.classList.remove("hide");
  alertElement.classList.add("show");

  setTimeout(() => {
    alertElement.classList.remove("show");
    alertElement.classList.add("hide");
  }, 3000);
}

function startVoiceInput() {
  if ('webkitSpeechRecognition' in window) {
    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = function () {
      document.getElementById('audioInputBtn').innerText = 'Listening...';
    };

    recognition.onresult = function (event) {
      const voiceInput = event.results[0][0].transcript;
      document.getElementById('question').value = voiceInput;
      document.getElementById('audioInputBtn').innerText = '🎤 Voice Input';
    };

    recognition.onerror = function () {
      document.getElementById('audioInputBtn').innerText = '🎤 Voice Input';
      alert('Voice recognition failed. Please try again.');
    };

    recognition.start();
  } else {
    alert('Voice recognition not supported in this browser.');
  }
}
