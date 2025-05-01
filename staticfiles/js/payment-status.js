/**
 * Script para manejar la verificación automática del estado de pagos
 * y mejorar la experiencia de usuario durante el proceso de pago con QR
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM relacionados con pagos
    const paymentBlock = document.querySelector('.payment-block');
    const paymentStatus = document.querySelector('.payment-status');
    const fileInput = document.getElementById('comprobante');
    const fileUploadForm = document.querySelector('.comprobante-form');
    const fileUploadLabel = document.querySelector('.file-upload label');

    // Verificar si estamos en la página de detalles de pago
    if (paymentStatus && paymentStatus.classList.contains('status-pendiente') || 
        paymentStatus && paymentStatus.classList.contains('status-procesando')) {
        
        // Configurar verificación periódica del estado (cada 30 segundos)
        const pedidoId = getPedidoIdFromPage();
        if (pedidoId) {
            // Primera verificación después de 30 segundos
            setTimeout(() => {
                checkPaymentStatus(pedidoId);
            }, 30000);
        }
    }

    // Mejorar experiencia de usuario en formulario de comprobante
    if (fileInput) {
        // Mostrar nombre del archivo seleccionado
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const fileName = this.files[0].name;
                if (fileUploadLabel) {
                    fileUploadLabel.textContent = fileName.length > 20 
                        ? fileName.substring(0, 17) + '...' 
                        : fileName;
                }
                
                // Vista previa de la imagen
                showImagePreview(this.files[0]);
            }
        });

        // Mejorar formulario con validación y feedback
        if (fileUploadForm) {
            fileUploadForm.addEventListener('submit', function(e) {
                // Solo validar que haya un archivo
                if (!fileInput.files || fileInput.files.length === 0) {
                    e.preventDefault();
                    showFormError(fileInput, 'Por favor selecciona un comprobante');
                } else {
                    // Validar tipo de archivo (solo imágenes)
                    const fileType = fileInput.files[0].type;
                    if (!fileType.startsWith('image/')) {
                        e.preventDefault();
                        showFormError(fileInput, 'Solo se permiten archivos de imagen');
                    } else {
                        // Mostrar estado de carga
                        const submitBtn = this.querySelector('button[type="submit"]');
                        if (submitBtn) {
                            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Subiendo...';
                            submitBtn.disabled = true;
                        }
                    }
                }
            });
        }
    }

    // Función para obtener el ID del pedido desde la página
    function getPedidoIdFromPage() {
        // Buscar el ID en el contenido de la página
        const orderNumberEl = document.querySelector('.order-number strong');
        if (orderNumberEl) {
            const orderText = orderNumberEl.textContent;
            // Extraer el número del formato "#12345"
            const match = orderText.match(/#(\d+)/);
            if (match && match[1]) {
                return match[1];
            }
        }
        return null;
    }

    // Función para verificar el estado del pago mediante AJAX
    function checkPaymentStatus(pedidoId) {
        fetch(`/pedidos/verificar-pago/${pedidoId}/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Si el estado del pago ha cambiado, actualizar la UI
                if (data.estado !== paymentStatus.dataset.estado) {
                    updatePaymentStatusUI(data.estado, data.mensaje);
                    
                    // Si el pago está completado, detener las verificaciones
                    if (data.estado === 'completado') {
                        return;
                    }
                }
                
                // Programar la siguiente verificación en 30 segundos
                setTimeout(() => {
                    checkPaymentStatus(pedidoId);
                }, 30000);
            }
        })
        .catch(error => {
            console.error('Error al verificar estado del pago:', error);
            // Reintentar después de un tiempo más largo
            setTimeout(() => {
                checkPaymentStatus(pedidoId);
            }, 60000);
        });
    }

    // Función para actualizar la UI según el estado del pago
    function updatePaymentStatusUI(estado, mensaje) {
        // Actualizar clase de estado
        paymentStatus.className = 'payment-status status-' + estado;
        
        // Actualizar el indicador visual
        const statusText = paymentStatus.querySelector('.status-text');
        if (statusText) {
            switch (estado) {
                case 'pendiente':
                    statusText.textContent = 'Pendiente';
                    break;
                case 'procesando':
                    statusText.textContent = 'Procesando';
                    break;
                case 'completado':
                    statusText.textContent = 'Completado';
                    break;
                case 'fallido':
                    statusText.textContent = 'Fallido';
                    break;
                default:
                    statusText.textContent = estado;
            }
        }
        
        // Actualizar mensaje si se proporciona
        if (mensaje) {
            const messageEl = document.querySelector('.payment-message');
            if (messageEl) {
                messageEl.textContent = mensaje;
                
                // Actualizar clase del mensaje según estado
                messageEl.className = 'payment-message';
                if (estado === 'completado') {
                    messageEl.classList.add('success');
                } else if (estado === 'fallido') {
                    messageEl.classList.add('error');
                } else {
                    messageEl.classList.add('warning');
                }
            }
        }
        
        // Si el pago está completado, ocultar el formulario de comprobante
        if (estado === 'completado' && fileUploadForm) {
            fileUploadForm.style.display = 'none';
            
            // Mostrar mensaje de éxito
            const uploadSection = document.querySelector('.qr-upload-section');
            if (uploadSection) {
                uploadSection.innerHTML = '<div class="payment-message success">' +
                    '<i class="fas fa-check-circle"></i> ' +
                    'El pago ha sido confirmado. ¡Gracias por tu compra!</div>';
            }
            
            // Recargar la página después de un breve retraso para mostrar los detalles actualizados
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        }
        
        // Guardar el estado actual para comparaciones futuras
        paymentStatus.dataset.estado = estado;
    }

    // Mostrar una vista previa de la imagen seleccionada
    function showImagePreview(file) {
        // Crear un contenedor para la vista previa si no existe
        let previewContainer = document.querySelector('.comprobante-preview');
        
        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.className = 'comprobante-preview';
            previewContainer.style.marginTop = '15px';
            previewContainer.style.textAlign = 'center';
            fileUploadForm.insertBefore(previewContainer, fileUploadForm.querySelector('button'));
        } else {
            // Limpiar vista previa anterior
            previewContainer.innerHTML = '';
        }

        // Crear elemento de imagen para la vista previa
        const img = document.createElement('img');
        img.style.maxWidth = '100%';
        img.style.maxHeight = '200px';
        img.style.border = '1px solid #ddd';
        img.style.borderRadius = '4px';
        img.style.padding = '5px';
        previewContainer.appendChild(img);

        // Leer el archivo y mostrar la vista previa
        const reader = new FileReader();
        reader.onload = function(e) {
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    // Mostrar mensaje de error en el formulario
    function showFormError(inputElement, message) {
        // Eliminar mensajes de error anteriores
        const existingError = inputElement.parentElement.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Crear y mostrar el nuevo mensaje de error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = message;
        inputElement.parentElement.appendChild(errorDiv);
        
        // Resaltar el input con error
        inputElement.classList.add('error');
        
        // Eliminar el error cuando el usuario corrija el problema
        inputElement.addEventListener('change', function() {
            this.classList.remove('error');
            const error = this.parentElement.querySelector('.form-error');
            if (error) {
                error.remove();
            }
        }, { once: true });
    }
    
    // Función para obtener cookie (para CSRF token)
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