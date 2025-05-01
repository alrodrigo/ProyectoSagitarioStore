/**
 * Sagitario Store - Funcionalidades para la página de categorías
 * Maneja el cambio de vista y errores de carga de imágenes
 */

document.addEventListener('DOMContentLoaded', function() {
    // View toggle functionality
    const gridBtn = document.querySelector('.view-btn.grid');
    const listBtn = document.querySelector('.view-btn.list');
    const productsContainer = document.querySelector('.products-container');
    
    if (gridBtn && listBtn && productsContainer) {
        gridBtn.addEventListener('click', function() {
            productsContainer.classList.remove('list-view');
            gridBtn.classList.add('active');
            listBtn.classList.remove('active');
            localStorage.setItem('productsView', 'grid');
        });
        
        listBtn.addEventListener('click', function() {
            productsContainer.classList.add('list-view');
            listBtn.classList.add('active');
            gridBtn.classList.remove('active');
            localStorage.setItem('productsView', 'list');
        });
        
        // Restore view preference
        const savedView = localStorage.getItem('productsView');
        if (savedView === 'list') {
            listBtn.click();
        }
    }
    
    // Sorting functionality
    const sortSelect = document.getElementById('sort-by');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('sort', this.value);
            window.location.href = currentUrl.toString();
        });
    }
});