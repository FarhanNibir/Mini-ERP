
document.addEventListener("DOMContentLoaded", function () {

    // ==============================
    // 1. LIGHT / DARK THEME
    // ==============================

    const themeToggle = document.getElementById("themeToggle");
    const themeIcon = document.getElementById("themeIcon");
    const html = document.documentElement;

    // Load saved theme (default: light)
    const savedTheme = localStorage.getItem("erp-theme") || "light";

    applyTheme(savedTheme);

    function applyTheme(theme) {
        html.setAttribute("data-theme", theme);
        localStorage.setItem("erp-theme", theme);

        if (themeIcon) {
            themeIcon.className = theme === "dark"
                ? "bi bi-sun"
                : "bi bi-moon-stars";
        }
    }

    if (themeToggle) {
        themeToggle.addEventListener("click", function () {
            const currentTheme = html.getAttribute("data-theme");
            const newTheme = currentTheme === "dark" ? "light" : "dark";

            applyTheme(newTheme);
        });
    }


    // ==============================
    // 2. SIDEBAR TOGGLE
    // ==============================

    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", function () {
            sidebar.classList.toggle("show");
        });
    }

});
