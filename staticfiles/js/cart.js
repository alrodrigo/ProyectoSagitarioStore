function updateQuantity(button, change) {
    const form = button.closest('.quantity-form');
    const input = form.querySelector('input[name="quantity"]');
    const currentValue = parseInt(input.value);
    const maxValue = parseInt(input.getAttribute('max'));
    const newValue = currentValue + change;

    if (newValue >= 1 && newValue <= maxValue) {
        input.value = newValue;
        form.submit();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Auto-submit quantity changes
    const quantityForms = document.querySelectorAll('.quantity-form');
    quantityForms.forEach(form => {
        const input = form.querySelector('input[name="quantity"]');
        let timeout;

        input.addEventListener('change', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => form.submit(), 500);
        });
    });

    // Animación para eliminación de productos
    const removeButtons = document.querySelectorAll('.remove-item');
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const item = this.closest('.cart-item');
            item.style.animation = 'slideOut 0.3s ease-out';
            
            setTimeout(() => {
                this.closest('form').submit();
            }, 300);
        });
    });
});