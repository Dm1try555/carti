function changeMainImage(src, thumbnail) {
    document.getElementById('mainProductImage').src = src;
    document.querySelectorAll('.thumbnail').forEach(thumb => thumb.classList.remove('active'));
    thumbnail.classList.add('active');
}

function changeQuantity(delta) {
    const input = document.getElementById('quantityInput');
    let quantity = parseInt(input.value) + delta;
    const max = parseInt(input.max);

    if (quantity < 1) quantity = 1;
    if (quantity > max) quantity = max;

    input.value = quantity;
}

function showTab(tabName, event) {
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}


function toggleWishlist(productId) {
    // Функція додавання у вибране
    console.log('Перемикання вибраного для товару:', productId);
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