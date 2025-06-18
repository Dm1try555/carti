document.addEventListener("DOMContentLoaded", function () {
    const dropdownBtn = document.querySelector(".dropbtn");
    const dropdown = document.querySelector(".dropdown");

    dropdownBtn.addEventListener("click", function (e) {
        e.preventDefault();
        dropdown.classList.toggle("open");
    });

    // Закриття при кліку поза меню
    document.addEventListener("click", function (e) {
        if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
        }
    });
});