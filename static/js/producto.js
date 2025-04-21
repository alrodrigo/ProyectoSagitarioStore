document.addEventListener('DOMContentLoaded', function() {
    // Manejo de imágenes y miniaturas
    const mainImage = document.getElementById('imagen-principal');
    const thumbnails = document.querySelectorAll('.miniatura');
    
    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function() {
            // Actualizar imagen principal
            mainImage.src = this.src;
            // Actualizar clase activa
            thumbnails.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Selector de cantidad
    const minusBtn = document.querySelector('.cantidad-btn.menos');
    const plusBtn = document.querySelector('.cantidad-btn.mas');
    const quantityInput = document.querySelector('input[name="cantidad"]');
    
    if (quantityInput) {
        const maxStock = parseInt(quantityInput.getAttribute('max') || '999');

        minusBtn?.addEventListener('click', () => {
            const currentValue = parseInt(quantityInput.value);
            if (currentValue > 1) {
                quantityInput.value = currentValue - 1;
            }
        });

        plusBtn?.addEventListener('click', () => {
            const currentValue = parseInt(quantityInput.value);
            if (currentValue < maxStock) {
                quantityInput.value = currentValue + 1;
            }
        });
    }
    
    // Botón de lista de deseos
    const wishlistBtn = document.querySelector('.btn-wishlist');
    wishlistBtn?.addEventListener('click', function() {
        this.classList.toggle('active');
        const icon = this.querySelector('i');
        if (this.classList.contains('active')) {
            icon.classList.remove('far');
            icon.classList.add('fas');
            showNotification('Producto añadido a favoritos', 'success');
        } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
            showNotification('Producto eliminado de favoritos', 'success');
        }
    });

    // Función para mostrar notificaciones
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }, 2000);
        }, 100);
    }
});