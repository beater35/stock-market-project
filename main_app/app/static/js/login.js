document.addEventListener("DOMContentLoaded", function () {
  const loginTab = document.getElementById("loginTab");
  const signupTab = document.getElementById("signupTab");
  const loginForm = document.getElementById("loginForm");
  const signupForm = document.getElementById("signupForm");
  const underline = document.querySelector(".underline");

  function showLogin() {
      loginForm.classList.remove("hidden");
      signupForm.classList.add("hidden");
      loginTab.classList.add("active");
      signupTab.classList.remove("active");
      underline.style.transform = "translateX(0%)";
  }

  function showSignup() {
      loginForm.classList.add("hidden");
      signupForm.classList.remove("hidden");
      loginTab.classList.remove("active");
      signupTab.classList.add("active");
      underline.style.transform = "translateX(100%)";
  }

  // Ensure correct tab is shown on page load
  showLogin();

  // Attach event listeners
  loginTab.addEventListener("click", showLogin);
  signupTab.addEventListener("click", showSignup);
});

document.addEventListener("DOMContentLoaded", function () {
  setTimeout(function () {
      let messages = document.querySelectorAll(".flash-message");
      messages.forEach(function (msg) {
          msg.style.opacity = "0";
          setTimeout(() => msg.remove(), 500);
      });
  }, 3000);
});
