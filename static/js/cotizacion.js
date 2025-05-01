document.addEventListener('DOMContentLoaded', function() {
    // Previsualizar imagen
    const imagenInput = document.getElementById('imagenProducto');
    const imagenPreview = document.getElementById('imagenPreview');
    const imageOptions = document.getElementById('imageOptions');
    const downloadLink = document.getElementById('downloadImage');
    const stepInstructions = document.getElementById('stepInstructions');
    let imageBase64 = '';
    
    imagenInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagenPreview.src = e.target.result;
                imagenPreview.style.display = 'block';
                imageOptions.style.display = 'block';
                stepInstructions.style.display = 'block';
                
                // Guardar la imagen en formato Base64
                imageBase64 = e.target.result;
                
                // Configurar el enlace de descarga
                downloadLink.href = imageBase64;
            }
            reader.readAsDataURL(file);
        } else {
            imagenPreview.src = "#";
            imagenPreview.style.display = 'none';
            imageOptions.style.display = 'none';
            stepInstructions.style.display = 'none';
        }
    });
    
    // Enviar formulario a WhatsApp
    const form = document.getElementById('cotizacionForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Recopilar datos del formulario
        const nombreProducto = document.getElementById('nombreProducto').value;
        const codigoProducto = document.getElementById('codigoProducto').value;
        const descripcion = document.getElementById('descripcion').value;
        const nombreCliente = document.getElementById('nombreCliente').value;
        const telefonoCliente = document.getElementById('telefonoCliente').value;
        
        // Crear mensaje para WhatsApp
        let mensaje = `*SOLICITUD DE COTIZACIÓN*%0A%0A`;
        mensaje += `*Producto:* ${nombreProducto}%0A`;
        if (codigoProducto) {
            mensaje += `*Código:* ${codigoProducto}%0A`;
        }
        mensaje += `*Descripción:* ${descripcion}%0A%0A`;
        
        // Indicar si se enviará una imagen por separado
        if (imagenPreview.style.display !== 'none') {
            mensaje += `*Nota:* Te enviaré una imagen de referencia en un momento.%0A%0A`;
        }
        
        mensaje += `*Datos del cliente:*%0A`;
        mensaje += `*Nombre:* ${nombreCliente}%0A`;
        mensaje += `*Teléfono:* ${telefonoCliente}%0A`;
        
        // Número de WhatsApp del administrador (usar el que está en el footer)
        const whatsappAdmin = "59170000000";
        
        // Crear enlace de WhatsApp y redirigir
        const whatsappUrl = `https://wa.me/${whatsappAdmin}?text=${mensaje}`;
        window.open(whatsappUrl, '_blank');
        
        // No resetear el formulario inmediatamente para permitir que el usuario descargue la imagen
        // Solo mostramos un mensaje
        alert('Tu solicitud de cotización ha sido enviada. No olvides adjuntar la imagen de referencia en WhatsApp si has incluido una.');
    });
});