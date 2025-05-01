document.addEventListener('DOMContentLoaded', function() {
    // Controles de vista (grid/list)
    const viewButtons = document.querySelectorAll('.view-btn');
    const productsContainer = document.querySelector('.products-container');
    
    viewButtons.forEach(button => {
        button.addEventListener('click', () => {
            viewButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            if (button.classList.contains('list')) {
                productsContainer.classList.add('list-view');
            } else {
                productsContainer.classList.remove('list-view');
            }
        });
    });

    // Ordenamiento de productos
    const sortSelect = document.getElementById('sort-by');
    sortSelect.addEventListener('change', function() {
        const url = new URL(window.location);
        url.searchParams.set('sort', this.value);
        window.location = url;
    });

    // Funcionalidad de añadir al carrito
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            try {
                const response = await fetch('/pedidos/agregar_al_carrito/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        product_id: productId,
                        quantity: 1
                    })
                });
                
                if (response.ok) {
                    // Actualizar el contador del carrito
                    const cartCount = document.querySelector('.cart-count');
                    const data = await response.json();
                    cartCount.textContent = data.total_items;
                    
                    // Mostrar mensaje de éxito
                    showNotification('Producto añadido al carrito', 'success');
                } else {
                    showNotification('Error al añadir al carrito', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('Error al añadir al carrito', 'error');
            }
        });
    });

    // Función auxiliar para obtener el token CSRF
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