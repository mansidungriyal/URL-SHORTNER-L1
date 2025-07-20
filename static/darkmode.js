
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("darkModeToggle");
  const themeIcon = document.getElementById("theme-icon");

  function enableDarkMode() {
    document.body.classList.add("dark-mode");
    localStorage.setItem("darkMode", "enabled");
    themeIcon.textContent = "☀️";
  }

  function disableDarkMode() {
    document.body.classList.remove("dark-mode");
    localStorage.setItem("darkMode", "disabled");
    themeIcon.textContent = "🌙";
  }

  if (localStorage.getItem("darkMode") === "enabled") {
    toggle.checked = true;
    enableDarkMode();
  } else {
    disableDarkMode();
  }

  toggle.addEventListener("change", () => {
    if (toggle.checked) {
      enableDarkMode();
    } else {
      disableDarkMode();
    }
  });
});

function copyToClipboard(text) {
  navigator.clipboard.writeText(text)
    .then(() => alert("Link copied to clipboard!"))
    .catch(err => console.error("Failed to copy: ", err));
}

