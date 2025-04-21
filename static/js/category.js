/**
 * Sagitario Store - Funcionalidades para la página de categorías
 * Maneja el cambio de vista y errores de carga de imágenes
 */

document.addEventListener('DOMContentLoaded', function() {
    // Funcionalidad para cambiar entre vistas de cuadrícula y lista
    const gridButton = document.querySelector('.view-btn.grid');
    const listButton = document.querySelector('.view-btn.list');
    const productsContainer = document.querySelector('.products-container');
    
    if (gridButton && listButton && productsContainer) {
        gridButton.addEventListener('click', function() {
            productsContainer.classList.remove('list-view');
            gridButton.classList.add('active');
            listButton.classList.remove('active');
            // Guardar preferencia en localStorage
            localStorage.setItem('category-view', 'grid');
        });
        
        listButton.addEventListener('click', function() {
            productsContainer.classList.add('list-view');
            listButton.classList.add('active');
            gridButton.classList.remove('active');
            // Guardar preferencia en localStorage
            localStorage.setItem('category-view', 'list');
        });
        
        // Recuperar vista preferida del usuario
        const savedView = localStorage.getItem('category-view');
        if (savedView === 'list') {
            productsContainer.classList.add('list-view');
            listButton.classList.add('active');
            gridButton.classList.remove('active');
        }
    }
    
    // Manejo mejorado de errores en carga de imágenes
    const productImages = document.querySelectorAll('.img-product img');
    
    productImages.forEach(img => {
        // Añadir clase loading al contenedor mientras carga la imagen
        const imgContainer = img.closest('.img-product');
        if (imgContainer && !img.complete) {
            imgContainer.classList.add('loading');
        }
        
        // Marcar como loaded cuando la imagen cargue correctamente
        img.addEventListener('load', function() {
            const container = this.closest('.img-product');
            if (container) {
                container.classList.remove('loading');
                // Asegurar que la imagen sea visible
                this.style.opacity = '1';
                // Eliminar clase error si existe
                this.classList.remove('error');
            }
        });
        
        // Manejar errores de carga de imagen
        img.addEventListener('error', function() {
            console.log('Error cargando imagen:', this.src);
            
            // Añadir clase error para activar CSS de fallback
            this.classList.add('error');
            
            const container = this.closest('.img-product');
            if (container) {
                container.classList.remove('loading');
                
                // Disparar un evento personalizado para que otros scripts puedan reaccionar
                container.dispatchEvent(new CustomEvent('image-error', {
                    bubbles: true,
                    detail: { imgSrc: this.src }
                }));
            }
        });
        
        // Si la imagen ya está en el DOM, verificar su estado
        if (img.complete) {
            if (img.naturalHeight === 0 || img.naturalWidth === 0) {
                // La imagen falló al cargar
                img.dispatchEvent(new Event('error'));
            } else {
                // La imagen ya estaba cargada
                img.dispatchEvent(new Event('load'));
            }
        }
    });
    
    // Funcionalidad para ordenar productos
    const sortSelect = document.getElementById('sort-by');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const value = this.value;
            const url = new URL(window.location.href);
            
            // Actualizar parámetro de orden en la URL
            url.searchParams.set('sort', value);
            
            // Mantener el parámetro de paginación si existe
            const currentPage = url.searchParams.get('page');
            if (currentPage) {
                url.searchParams.set('page', '1'); // Volver a la primera página al cambiar el orden
            }
            
            // Redirigir a la URL actualizada
            window.location.href = url.toString();
        });
        
        // Establecer el valor seleccionado basado en la URL
        const urlParams = new URLSearchParams(window.location.search);
        const sortParam = urlParams.get('sort');
        if (sortParam) {
            sortSelect.value = sortParam;
        }
    }
});