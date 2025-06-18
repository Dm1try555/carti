// Обробка зміни способу доставки
document.querySelectorAll('input[name="delivery_method"]').forEach(radio => {
    radio.addEventListener('change', function() {
        const deliveryAddress = document.getElementById('deliveryAddress');
        const deliveryCost = document.getElementById('deliveryCost');
        const finalTotal = document.getElementById('finalTotal');
        
        if (this.value === 'pickup') {
            deliveryAddress.style.display = 'none';
            deliveryCost.textContent = 'Безкоштовно';
            // Оновити підрахунок суми
        } else {
            deliveryAddress.style.display = 'block';
            deliveryCost.textContent = '300 ₽';
            // Оновити підрахунок суми
        }
    });
});

// Валідація форми
document.querySelector('.checkout-form').addEventListener('submit', function(e) {
    const requiredFields = this.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('error');
            isValid = false;
        } else {
            field.classList.remove('error');
        }
    });
    
    if (!isValid) {
        e.preventDefault();
        showMessage('Будь ласка, заповніть всі обов\'язкові поля', 'error');
    }
});

// Форматування номера телефону
document.getElementById('phone').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length > 0) {
        if (value[0] === '8') value = '7' + value.slice(1);
        if (value[0] === '7') {
            value = value.slice(0, 11);
            const formatted = '+7 (' + value.slice(1, 4) + ') ' + value.slice(4, 7) + '-' + value.slice(7, 9) + '-' + value.slice(9, 11);
            e.target.value = formatted;
        }
    }
});