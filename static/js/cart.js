function updateCartQuantity(productId, newQuantity) {
    if (newQuantity < 1) {
        removeFromCart(productId);
        return;
    }

    fetch('{% url "cart:update_cart" %}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: newQuantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            showMessage(data.message || 'Помилка при оновленні кошика', 'error');
        }
    })
    .catch(error => {
        showMessage('Виникла помилка', 'error');
    });
}

function removeFromCart(productId) {
    if (confirm('Видалити товар з кошика?')) {
        fetch('{% url "cart:remove_from_cart" %}', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                product_id: productId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                showMessage(data.message || 'Помилка при видаленні товару', 'error');
            }
        })
        .catch(error => {
            showMessage('Виникла помилка', 'error');
        });
    }
}