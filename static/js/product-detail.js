document.addEventListener('DOMContentLoaded', function() {
    // Manejo de tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            
            // Actualizar botones
            tabBtns.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Actualizar paneles
            tabPanels.forEach(panel => {
                if (panel.id === tabId) {
                    panel.classList.add('active');
                } else {
                    panel.classList.remove('active');
                }
            });
        });
    });

    // Manejo de galería de imágenes
    function changeMainImage(src) {
        const mainImg = document.getElementById('mainProductImage');
        mainImg.style.opacity = '0';
        
        setTimeout(() => {
            mainImg.src = src;
            mainImg.style.opacity = '1';
        }, 300);
    }

    // Manejo de cantidad
    const quantityInput = document.getElementById('quantity');
    
    function updateQuantity(change) {
        const currentValue = parseInt(quantityInput.value);
        const maxValue = parseInt(quantityInput.getAttribute('max'));
        const newValue = currentValue + change;
        
        if (newValue >= 1 && newValue <= maxValue) {
            quantityInput.value = newValue;
        }
    }

    // Sistema de rating
    const ratingInputs = document.querySelectorAll('.star-rating input');
    const ratingLabels = document.querySelectorAll('.star-rating label');

    ratingInputs.forEach((input, index) => {
        input.addEventListener('change', function() {
            ratingLabels.forEach((label, labelIndex) => {
                if (labelIndex <= index) {
                    label.querySelector('i').className = 'fas fa-star';
                } else {
                    label.querySelector('i').className = 'far fa-star';
                }
            });
        });
    });

    // Exponer funciones globalmente
    window.changeMainImage = changeMainImage;
    window.updateQuantity = updateQuantity;
});