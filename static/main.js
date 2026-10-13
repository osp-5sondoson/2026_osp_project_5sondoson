// Show a preview of the selected picture on the registration page
const fileInput = document.getElementById("file_input");
const preview = document.getElementById("preview");

if (fileInput && preview) {
  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) {
      preview.style.display = "none";
      return;
    }
    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";
  });
}
