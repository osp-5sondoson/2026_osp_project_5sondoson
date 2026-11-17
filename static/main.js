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

/* =========================================================
   아직 만들지 않은 기능 안내
   data-soon="기능 이름" 이 붙은 링크·버튼을 누르면 "준비 중" 알림만 띄움
   (거래 가이드 · 자주 묻는 질문 · 비밀번호 찾기 · 구매하기)
   ========================================================= */

document.querySelectorAll("[data-soon]").forEach((element) => {
  element.addEventListener("click", (event) => {
    event.preventDefault();
    const feature = element.dataset.soon;
    const message =
      feature === "구매"
        ? "구매 기능은 준비 중이에요.\n지금은 상세 페이지의 판매자 이메일로 연락해 주세요."
        : feature + " 페이지는 준비 중이에요.";
    alert(message);
  });
});


/* =========================================================
   좋아요 (상품 상세)
   data-like-url 버튼을 누르면 AJAX(fetch)로 서버에 알리고,
   페이지를 새로 고치지 않고 버튼 모양과 숫자만 바꿈
   처음 누르면 좋아요, 다시 누르면 취소 (로그인한 사용자별로 DB에 저장)
   ========================================================= */

document.querySelectorAll("[data-like-url]").forEach((button) => {
  const icon = button.querySelector(".like-button__icon");
  const count = button.querySelector(".like-button__count");

  button.addEventListener("click", async () => {
    button.disabled = true;
    try {
      const response = await fetch(button.dataset.likeUrl, { method: "POST" });
      const result = await response.json();

      if (response.status === 401) {
        alert("좋아요를 누르려면 로그인해 주세요.");
        window.location.href = result.login_url;
        return;
      }
      if (!response.ok) {
        alert(result.error || "좋아요를 처리하지 못했어요. 잠시 후 다시 시도해 주세요.");
        return;
      }

      button.classList.toggle("is-liked", result.liked);
      button.setAttribute("aria-pressed", String(result.liked));
      icon.textContent = result.liked ? "♥" : "♡";
      count.textContent = result.count;
    } catch (error) {
      alert("좋아요를 처리하지 못했어요. 잠시 후 다시 시도해 주세요.");
    } finally {
      button.disabled = false;
    }
  });
});
