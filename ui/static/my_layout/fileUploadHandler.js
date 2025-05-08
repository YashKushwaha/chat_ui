// --- FILE UPLOAD HANDLING ---
export async function handleFileUpload() {
    const fileInput = document.getElementById("file-upload");
  
    fileInput.addEventListener("change", async function () {
      const file = this.files[0];
      if (!file) return;
  
      const formData = new FormData();
      formData.append("file", file);
  
      try {
        const response = await fetch("/upload", {
          method: "POST",
          body: formData,
        });
  
        const result = await response.json();
        alert(result.message); // or update the UI
      } catch (error) {
        console.error("Upload failed:", error);
        alert("Upload failed. Please try again.");
      }
  
      this.value = ""; // reset file input
    });
  }
  