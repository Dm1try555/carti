function updateSort(sortValue) {
    const url = new URL(window.location);
    url.searchParams.set('sort', sortValue);
    window.location.href = url.toString();
}

document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('filtersToggleBtn');
    const filtersSection = document.querySelector('.filters-section');

    toggleBtn.addEventListener('click', function () {
        filtersSection.classList.toggle('active');
    });
});
