document.addEventListener("DOMContentLoaded", function() {
    const lightBtn = document.getElementById("lightMode");
    const softBtn = document.getElementById("softMode");
    const darkBtn = document.getElementById("darkMode");

    function setTheme(theme) {
        document.body.classList.remove("light-theme", "soft-theme", "dark-theme");
        document.body.classList.add(theme);
        localStorage.setItem("theme", theme);
    }

    lightBtn.addEventListener("click", () => setTheme("light-theme"));
    softBtn.addEventListener("click", () => setTheme("soft-theme"));
    darkBtn.addEventListener("click", () => setTheme("dark-theme"));

    // Persist theme on page reload
    const savedTheme = localStorage.getItem("theme") || "light-theme";
    document.body.classList.add(savedTheme);
});