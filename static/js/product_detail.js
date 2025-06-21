function changeMainImage(src, thumbnail) {
    document.getElementById('mainProductImage').src = src;
    document.querySelectorAll('.thumbnail').forEach(thumb => thumb.classList.remove('active'));
    thumbnail.classList.add('active');
}


let galleryImages = [];
let currentImageIndex = 0;

// При клике на миниатюру — просто меняем главное изображение
function changeMainImage(src, thumbnail) {
    document.getElementById('mainProductImage').src = src;
    document.querySelectorAll('.thumbnail').forEach(t => t.classList.remove('active'));
    thumbnail.classList.add('active');

    // Обновим текущий индекс
    currentImageIndex = galleryImages.indexOf(src);
}

// При клике по главному изображению — откроется модальное
function openImageModal() {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    const currentSrc = document.getElementById('mainProductImage').src;

    currentImageIndex = galleryImages.indexOf(currentSrc);
    modal.style.display = 'flex';
    modalImg.src = currentSrc;
}

function closeImageModal() {
    document.getElementById('imageModal').style.display = 'none';
}

// Перелистывание изображений
function changeModalImage(direction) {
    if (galleryImages.length === 0) return;

    currentImageIndex += direction;
    if (currentImageIndex < 0) currentImageIndex = galleryImages.length - 1;
    if (currentImageIndex >= galleryImages.length) currentImageIndex = 0;

    document.getElementById('modalImage').src = galleryImages[currentImageIndex];
    document.getElementById('mainProductImage').src = galleryImages[currentImageIndex];

    // Подсветим активную миниатюру
    document.querySelectorAll('.thumbnail').forEach(thumb => {
        thumb.classList.toggle('active', thumb.src === galleryImages[currentImageIndex]);
    });
}

// Собираем все изображения после загрузки
document.addEventListener('DOMContentLoaded', () => {
    galleryImages = Array.from(document.querySelectorAll('.thumbnail')).map(img => img.src);
    const mainImage = document.getElementById('mainProductImage').src;
    if (!galleryImages.includes(mainImage)) {
        galleryImages.unshift(mainImage);
    }
    currentImageIndex = galleryImages.indexOf(mainImage);
});




function closeImageModal() {
    document.getElementById('imageModal').style.display = 'none';
}

function changeQuantity(delta) {
    const input = document.getElementById('quantityInput');
    let quantity = parseInt(input.value) + delta;
    const max = parseInt(input.max);

    if (quantity < 1) quantity = 1;
    if (quantity > max) quantity = max;

    input.value = quantity;
}

function showTab(tabName, event = null) {
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
    if (event) {
        event.target.classList.add('active');
    } else {
        // Якщо немає event (наприклад, при ініціалізації)
        const defaultButton = document.querySelector(`[onclick*="${tabName}"]`);
        if (defaultButton) defaultButton.classList.add('active');
    }
}




// Обробка відправлення форми
document.getElementById('addToCartForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const productId = this.querySelector('[name="product_id"]').value;
    const quantity = this.querySelector('[name="quantity"]').value;
    const colorInput = this.querySelector('[name="color"]:checked');
    const sizeInput = this.querySelector('[name="size"]:checked');

    const data = {
        product_id: productId,
        quantity: quantity
    };

    if (colorInput) data.color = colorInput.value;
    if (sizeInput) data.size = sizeInput.value;

    fetch(this.action, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('Товар додано до корзини', 'success');
            updateCartCount(data.cart_count);
        } else {
            showMessage(data.message || 'Помилка при додаванні товару', 'error');
        }
    })
    .catch(error => {
        console.error(error);
        showMessage('Сталася помилка', 'error');
    });
});