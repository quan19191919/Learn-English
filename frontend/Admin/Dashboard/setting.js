// settings.js

function applyTheme() {
  const theme = localStorage.getItem("theme") || "light";
  if (theme === "dark") {
    document.body.classList.add("dark-mode");
    const btn = document.getElementById("themeToggleBtn");
    if (btn) btn.textContent = "🌞";
  } else {
    document.body.classList.remove("dark-mode");
    const btn = document.getElementById("themeToggleBtn");
    if (btn) btn.textContent = "🌙";
  }
}

function applyLanguage() {
  const lang = localStorage.getItem("language") || "vi";

  // Ví dụ dịch một số phần tử có id hoặc class cố định
  if (lang === "en") {
    document.querySelectorAll("[data-lang='dashboard']").forEach(el => el.textContent = "Dashboard");
    document.querySelectorAll("[data-lang='setting']").forEach(el => el.textContent = "Settings");
    // tiếp tục cho các key khác...
  } else {
    document.querySelectorAll("[data-lang='dashboard']").forEach(el => el.textContent = "Bảng điều khiển");
    document.querySelectorAll("[data-lang='setting']").forEach(el => el.textContent = "Cài đặt");
  }
}

window.addEventListener("DOMContentLoaded", () => {
  applyTheme();
  applyLanguage();
});
