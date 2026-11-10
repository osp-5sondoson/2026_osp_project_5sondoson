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


/* =========================================================
   비밀번호 보기 / 숨기기
   로그인 + 회원가입 공통
   ========================================================= */

document.querySelectorAll(".password-toggle").forEach((button) => {
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


/* =========================================================
   회원가입 비밀번호 일치 확인
   ========================================================= */

const signupPassword = document.getElementById("pw");
const signupPasswordConfirm = document.getElementById("pw_confirm");
const passwordMatchMessage = document.getElementById("pw-match-message");

function checkPasswordMatch() {
  if (
    !signupPassword ||
    !signupPasswordConfirm ||
    !passwordMatchMessage
  ) {
    return;
  }

  const password = signupPassword.value;
  const confirmPassword = signupPasswordConfirm.value;

  passwordMatchMessage.classList.remove(
    "is-match",
    "is-mismatch"
  );

  if (confirmPassword === "") {
    passwordMatchMessage.textContent = "";
    return;
  }

  if (password === confirmPassword) {
    passwordMatchMessage.textContent =
      "✓ 비밀번호가 일치해요.";

    passwordMatchMessage.classList.add("is-match");
  } else {
    passwordMatchMessage.textContent =
      "비밀번호가 일치하지 않아요.";

    passwordMatchMessage.classList.add("is-mismatch");
  }
}

if (signupPassword && signupPasswordConfirm) {
  signupPassword.addEventListener(
    "input",
    checkPasswordMatch
  );

  signupPasswordConfirm.addEventListener(
    "input",
    checkPasswordMatch
  );
}