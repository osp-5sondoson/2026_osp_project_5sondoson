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

document.querySelectorAll(".signup-password__toggle").forEach((button) => {
  button.addEventListener("click", () => {
    const targetId = button.dataset.target;
    const input = document.getElementById(targetId);

    if (!input) {
      return;
    }

    const willShowPassword = input.type === "password";

    if (willShowPassword) {
      input.type = "text";

      button.classList.add("is-visible");

      button.setAttribute("aria-label", "비밀번호 숨기기");
      button.setAttribute("aria-pressed", "true");
    } else {
      input.type = "password";

      button.classList.remove("is-visible");

      button.setAttribute("aria-label", "비밀번호 보기");
      button.setAttribute("aria-pressed", "false");
    }
  });
});

document.querySelectorAll(".login-password__toggle").forEach((button) => {
  button.addEventListener("click", () => {
    const targetId = button.dataset.target;
    const input = document.getElementById(targetId);

    if (!input) {
      return;
    }

    const willShowPassword = input.type === "password";

    if (willShowPassword) {
      input.type = "text";

      button.classList.add("is-visible");

      button.setAttribute("aria-label", "비밀번호 숨기기");
      button.setAttribute("aria-pressed", "true");
    } else {
      input.type = "password";

      button.classList.remove("is-visible");

      button.setAttribute("aria-label", "비밀번호 보기");
      button.setAttribute("aria-pressed", "false");
    }
  });
});