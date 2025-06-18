function updateSort(sortValue) {
    const url = new URL(window.location);
    url.searchParams.set('sort', sortValue);
    window.location.href = url.toString();
}

function setView(viewType) {
    const buttons = document.querySelectorAll('.view-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.closest('.view-btn').classList.add('active');
    
    const grid = document.getElementById('productsGrid');
    if (viewType === 'list') {
        grid.classList.add('list-view');
    } else {
        grid.classList.remove('list-view');
    }
    
    localStorage.setItem('catalogView', viewType);
}

// Відновлення вибору перегляду
document.addEventListener('DOMContentLoaded', function() {
    const savedView = localStorage.getItem('catalogView');
    if (savedView === 'list') {
        setView('list');
    }
});