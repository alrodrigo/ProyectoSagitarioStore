/**
 * product-card.js - Maneja la interactividad de las tarjetas de producto
 * Incluye: añadir al carrito, lista de deseos, vista rápida
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Función para mostrar notificaciones
    function showNotification(message, type = 'success') {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.innerHTML = message;
        
        // Añadir al contenedor de mensajes o crear uno si no existe
        let container = document.getElementById('messageContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'messageContainer';
            container.className = 'messages';
            document.body.prepend(container);
        }
        
        container.appendChild(notification);
        
        // Efecto de aparición
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Auto-eliminar después de 5 segundos
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                notification.remove();
                
                // Eliminar el contenedor si está vacío
                if (container.children.length === 0) {
                    container.remove();
                }
            }, 500);
        }, 5000);
    }
    
    // Función para actualizar el contador del carrito
    function updateCartCount() {
        fetch('/carrito/count/')
            .then(response => response.json())
            .then(data => {
                const cartCountElement = document.getElementById('cartCount');
                if (cartCountElement && data.count !== undefined) {
                    cartCountElement.textContent = data.count;
                    cartCountElement.classList.add('updated');
                    setTimeout(() => {
                        cartCountElement.classList.remove('updated');
                    }, 1000);
                }
            })
            .catch(error => console.error('Error al actualizar el contador del carrito:', error));
    }
    
    // Función para manejar el clic en botones de añadir al carrito
    function handleAddToCartClick(button) {
        // Verificar si el botón está deshabilitado
        if (button.classList.contains('disabled') || button.hasAttribute('disabled')) {
            showNotification('<i class="fas fa-exclamation-circle"></i> Producto agotado', 'warning');
            return;
        }
        
        const productId = button.getAttribute('data-product-id');
        
        // Añadir clase visual de carga (pueden ser diferentes según la clase del botón)
        if (button.classList.contains('btn--primary')) {
            button.classList.add('btn--loading');
        } else {
            button.classList.add('loading');
        }
        
        // Enviar solicitud AJAX para añadir al carrito
        fetch('/carrito/agregar-ajax/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken()
            },
            body: `product_id=${productId}&quantity=1`
        })
        .then(response => response.json())
        .then(data => {
            // Quitar animación de carga
            if (button.classList.contains('btn--loading')) {
                button.classList.remove('btn--loading');
            } 
            if (button.classList.contains('loading')) {
                button.classList.remove('loading');
            }
            
            if (data.success) {
                // Mostrar notificación de éxito
                showNotification('<i class="fas fa-check-circle"></i> Producto añadido al carrito', 'success');
                
                // Actualizar contador del carrito
                updateCartCount();
            } else {
                // Mostrar mensaje de error
                showNotification('<i class="fas fa-times-circle"></i> ' + (data.error || 'Error al añadir al carrito'), 'error');
            }
        })
        .catch(error => {
            console.error('Error al añadir al carrito:', error);
            // Quitar animación de carga
            if (button.classList.contains('btn--loading')) {
                button.classList.remove('btn--loading');
            } 
            if (button.classList.contains('loading')) {
                button.classList.remove('loading');
            }
            showNotification('<i class="fas fa-times-circle"></i> Error de conexión', 'error');
        });
    }
    
    // Manejar los botones de añadir al carrito en las tarjetas de producto (NUEVAS CLASES)
    const newAddToCartButtons = document.querySelectorAll('.product-card__btn.btn.btn--primary');
    newAddToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            handleAddToCartClick(this);
        });
    });
    
    // Manejar los botones de añadir al carrito (CLASES ANTIGUAS)
    const oldAddToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    oldAddToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            handleAddToCartClick(this);
        });
    });
    
    // Botones de lista de deseos (NUEVAS CLASES)
    const newWishlistButtons = document.querySelectorAll('.product-card__btn.btn.btn--outline-secondary');
    newWishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            handleWishlistClick(this);
        });
    });
    
    // Botones de lista de deseos (CLASES ANTIGUAS)
    const oldWishlistButtons = document.querySelectorAll('.wishlist-btn');
    oldWishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            handleWishlistClick(this);
        });
    });
    
    // Función para manejar clics de lista de deseos
    function handleWishlistClick(button) {
        const productId = button.getAttribute('data-product-id');
        const icon = button.querySelector('i');
        
        // Cambios visuales optimistas
        if (icon.classList.contains('far')) {
            icon.classList.replace('far', 'fas');
            showNotification('<i class="fas fa-heart"></i> Producto añadido a favoritos', 'success');
        } else {
            icon.classList.replace('fas', 'far');
            showNotification('<i class="fas fa-heart-broken"></i> Producto eliminado de favoritos', 'info');
        }
        
        // Enviar solicitud AJAX para toggle de wishlist
        fetch('/usuarios/wishlist/toggle/', {  // URL CORREGIDA
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken()
            },
            body: `product_id=${productId}`
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            if (!data.success) {
                // Si hay un error, revertir cambios visuales
                if (icon.classList.contains('fas')) {
                    icon.classList.replace('fas', 'far');
                } else {
                    icon.classList.replace('far', 'fas');
                }
                showNotification('<i class="fas fa-exclamation-circle"></i> ' + (data.error || 'Error al actualizar favoritos'), 'error');
            }
        })
        .catch(error => {
            console.error('Error al actualizar lista de deseos:', error);
            // Restaurar estado anterior en caso de error
            if (icon.classList.contains('fas')) {
                icon.classList.replace('fas', 'far');
            } else {
                icon.classList.replace('far', 'fas');
            }
            showNotification('<i class="fas fa-exclamation-circle"></i> Error de conexión', 'error');
        });
    }
    
    // Botones de vista rápida (NUEVAS CLASES)
    const newQuickViewButtons = document.querySelectorAll('.product-card__quick-view');
    newQuickViewButtons.forEach(button => {
        button.addEventListener('click', handleQuickView);
    });
    
    // Botones de vista rápida (CLASES ANTIGUAS)
    const oldQuickViewButtons = document.querySelectorAll('.quick-view-btn');
    oldQuickViewButtons.forEach(button => {
        button.addEventListener('click', handleQuickView);
    });
    
    // Función para manejar vista rápida
    function handleQuickView(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // Obtener información del producto del elemento padre
        let productCard = this.closest('.product-card');
        let productLink;
        
        if (productCard) {
            // Buscar enlaces en tarjetas nuevas
            productLink = productCard.querySelector('.product-card__link')?.href;
            
            // Si no lo encuentra, buscar con clases antiguas
            if (!productLink) {
                productLink = productCard.querySelector('.product-link')?.href;
            }
        }
        
        if (productLink) {
            // Redireccionar a la página del producto
            window.location.href = productLink;
        }
    }
    
    // Función para obtener el token CSRF
    function getCsrfToken() {
        const tokenElements = document.getElementsByName('csrfmiddlewaretoken');
        if (tokenElements.length > 0) {
            return tokenElements[0].value;
        }
        
        // Si no hay un input explícito, buscar en las cookies
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith('csrftoken=')) {
                return cookie.substring('csrftoken='.length);
            }
        }
        
        return null;
    }
});