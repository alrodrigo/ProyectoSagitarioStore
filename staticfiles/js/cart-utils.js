// Funciones para manejar el carrito y las notificaciones
document.addEventListener('DOMContentLoaded', function() {
    // Maneja los mensajes flash y los muestra como notificaciones
    const handleMessages = function() {
        const messages = document.querySelectorAll('.alert');
        if (messages.length > 0) {
            // Mostrar los mensajes uno por uno con un pequeño retraso entre ellos
            messages.forEach((message, index) => {
                setTimeout(() => {
                    // Primero asegurar que el mensaje sea visible
                    message.style.display = 'flex';
                    message.style.opacity = '1';
                    
                    // Después de 5 segundos, comenzar a ocultar
                    setTimeout(() => {
                        message.classList.add('fade-out');
                        setTimeout(() => {
                            message.remove();
                        }, 500);
                    }, 5000);
                }, index * 500); // Retraso entre mensajes
            });
        }
    };

    // Actualizar el contador del carrito
    const updateCartCount = function() {
        fetch('/carrito/count/')
            .then(response => response.json())
            .then(data => {
                const cartCountElement = document.getElementById('cartCount');
                if (cartCountElement && data.count !== undefined) {
                    // Actualizar el contador
                    cartCountElement.textContent = data.count;
                    
                    // Añadir efecto visual si el número cambió
                    const currentCount = parseInt(cartCountElement.textContent || '0');
                    if (currentCount !== data.count) {
                        cartCountElement.classList.add('updated');
                        setTimeout(() => {
                            cartCountElement.classList.remove('updated');
                        }, 2000);
                    }
                }
            })
            .catch(error => console.error('Error al actualizar el contador del carrito:', error));
    };
    
    // Función global para mostrar notificaciones en toda la aplicación
    window.showNotification = function(message, type = 'success') {
        // Crear contenedor de notificaciones si no existe
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        // Crear notificación
        const notification = document.createElement('div');
        notification.className = `toast toast--${type}`; // Usar clases consistentes
        notification.innerHTML = message;
        
        // Añadir al contenedor
        toastContainer.appendChild(notification);
        
        // Mostrar con animación
        setTimeout(() => {
            notification.classList.add('toast--visible');
        }, 100);
        
        // Ocultar después de 3 segundos
        setTimeout(() => {
            notification.classList.remove('toast--visible');
            notification.addEventListener('transitionend', () => {
                if (notification.parentElement) {
                    notification.parentElement.removeChild(notification);
                }
                // Eliminar contenedor si está vacío
                if (toastContainer.children.length === 0) {
                    document.body.removeChild(toastContainer);
                }
            }, { once: true });
        }, 3000);
    };
    
    // Manejar el formulario de añadir al carrito
    const addToCartForm = document.querySelector('.producto-compra');
    if (addToCartForm) {
        addToCartForm.addEventListener('submit', function() {
            // Solo guardamos una bandera para indicar que el formulario se ha enviado
            sessionStorage.setItem('cartUpdated', 'true');
        });
    }
    
    // Mostrar mensajes con animación
    handleMessages();
    
    // Siempre actualizar el contador del carrito al cargar la página
    updateCartCount();
    
    // Si hay un mensaje de éxito relacionado con el carrito o si la bandera de actualización está presente,
    // mostrar una animación adicional
    const messages = document.querySelectorAll('.alert-success');
    const hasCartMessage = Array.from(messages).some(msg => 
        msg.textContent.toLowerCase().includes('carrito') || msg.textContent.toLowerCase().includes('añadido')
    );
    
    if (hasCartMessage || sessionStorage.getItem('cartUpdated') === 'true') {
        // Limpiar la bandera
        sessionStorage.removeItem('cartUpdated');
        
        // Aplicar una animación extra
        const cartCountElement = document.getElementById('cartCount');
        if (cartCountElement) {
            cartCountElement.classList.add('updated');
            setTimeout(() => {
                cartCountElement.classList.remove('updated');
            }, 2000);
        }
    }
});

// Exportar las funciones para que sean accesibles globalmente
window.updateCartCount = function() {
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
};