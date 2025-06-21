function addToCart(productId, quantity = 1) {
    fetch(addToCartUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity,
        }),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.success) {
            showMessage("Товар додано до кошика", "success");
            updateCartCount(data.cart_count);
        } else {
            showMessage(data.message || "Помилка при додаванні товару", "error");
        }
    })
    .catch(() => {
        showMessage("Виникла помилка", "error");
    });
}

function getCSRFToken() {
    const token = document.querySelector("[name=csrfmiddlewaretoken]");
    return token ? token.value : "";
}

// ✅ Універсальний метод, який працює і через кнопки, і через input
function updateCartQuantity(productId, newQuantity = null) {
    const input = document.querySelector(`input[data-product-id="${productId}"]`);

    if (!input) {
        console.error("Поле input не знайдено для productId:", productId);
        return;
    }

    // Якщо не передали значення, читаємо з input
    const quantity = newQuantity !== null ? parseInt(newQuantity) : parseInt(input.value);

    if (isNaN(quantity) || quantity < 1) {
        removeFromCart(productId);
        return;
    }

    fetch(updateCartUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity,
        }),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.success) {
            location.reload();
        } else {
            showMessage(data.message || "Помилка при оновленні кошика", "error");
        }
    })
    .catch(() => {
        showMessage("Виникла помилка", "error");
    });
}

function removeFromCart(productId) {
    if (confirm("Видалити товар з кошика?")) {
        fetch(removeFromCartUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ product_id: productId }),
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                location.reload();
            } else {
                showMessage(data.message || "Помилка при видаленні товару", "error");
            }
        })
        .catch(() => {
            showMessage("Виникла помилка", "error");
        });
    }
}
