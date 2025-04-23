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
    wishlistBtn?.addEventListener('click', function(e) {
        e.preventDefault();
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

    // Manejo de formulario para añadir al carrito con AJAX
    const addToCartForm = document.querySelector('form.producto-compra');
    if (addToCartForm) {
        addToCartForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const productId = this.action.split('/').filter(Boolean).pop();
            const submitButton = this.querySelector('button[type="submit"]');
            const originalHTML = submitButton.innerHTML;
            
            // Verificar si el producto está agotado
            const stockInput = this.querySelector('input[name="cantidad"]');
            const maxStock = parseInt(stockInput.getAttribute('max') || '0');
            const quantity = parseInt(stockInput.value);
            
            if (maxStock <= 0) {
                showNotification('<i class="fas fa-times-circle"></i> Producto agotado', 'error');
                return;
            }
            
            if (quantity <= 0 || quantity > maxStock) {
                showNotification('<i class="fas fa-exclamation-circle"></i> Cantidad inválida', 'error');
                return;
            }
            
            // Mostrar indicador de carga
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
            submitButton.disabled = true;
            
            // Preparar datos para la petición
            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('quantity', quantity);
            
            // Realizar petición AJAX
            fetch('/carrito/agregar-ajax/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                // Restaurar estado original del botón
                submitButton.innerHTML = originalHTML;
                submitButton.disabled = false;
                
                if (data.success) {
                    showNotification('<i class="fas fa-check-circle"></i> Producto añadido al carrito', 'success');
                    
                    // Actualizar contador del carrito en el navbar si existe
                    const cartCountElement = document.querySelector('.cart-count');
                    if (cartCountElement && data.cart_count !== undefined) {
                        cartCountElement.textContent = data.cart_count;
                    }
                } else {
                    showNotification('<i class="fas fa-exclamation-circle"></i> ' + (data.error || 'Error al añadir al carrito'), 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                submitButton.innerHTML = originalHTML;
                submitButton.disabled = false;
                showNotification('<i class="fas fa-exclamation-circle"></i> Error de conexión', 'error');
            });
        });
    }
    
    // Productos relacionados - añadir al carrito rápido
    const quickBuyButtons = document.querySelectorAll('.productos-relacionados .producto-card .btn-quick-buy');
    quickBuyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = this.dataset.productId;
            if (!productId) return;
            
            // Mostrar indicador de carga
            const originalHTML = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            this.disabled = true;
            
            // Realizar petición AJAX
            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('quantity', 1);
            
            fetch('/carrito/agregar-ajax/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                // Restaurar estado original del botón
                this.innerHTML = originalHTML;
                this.disabled = false;
                
                if (data.success) {
                    showNotification('<i class="fas fa-check-circle"></i> Producto añadido al carrito', 'success');
                    
                    // Actualizar contador del carrito
                    const cartCountElement = document.querySelector('.cart-count');
                    if (cartCountElement && data.cart_count !== undefined) {
                        cartCountElement.textContent = data.cart_count;
                    }
                } else {
                    showNotification('<i class="fas fa-exclamation-circle"></i> ' + (data.error || 'Error al añadir al carrito'), 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.innerHTML = originalHTML;
                this.disabled = false;
                showNotification('<i class="fas fa-exclamation-circle"></i> Error de conexión', 'error');
            });
        });
    });

    // Función para mostrar notificaciones
    function showNotification(message, type) {
        // Crear el elemento de notificación
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = message;
        
        // Añadir al DOM
        document.body.appendChild(notification);
        
        // Mostrar con animación
        setTimeout(() => {
            notification.classList.add('show');
            
            // Ocultar después de un tiempo
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }, 3000);
        }, 100);
    }
    
    // Función para obtener cookies (CSRF token)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});