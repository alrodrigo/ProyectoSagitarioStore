document.addEventListener('DOMContentLoaded', () => {
    const mobileMenu = document.querySelector('.mobile-menu');
    const navbarNav = document.querySelector('.navbar__nav');
    const dropdownButtons = document.querySelectorAll('.dropdown__button');
    let isMenuOpen = false;

    // Toggle mobile menu
    mobileMenu?.addEventListener('click', () => {
        isMenuOpen = !isMenuOpen;
        navbarNav.classList.toggle('active');
        document.body.style.overflow = isMenuOpen ? 'hidden' : '';
        
        // Cerrar todos los dropdowns cuando se cierra el menú
        if (!isMenuOpen) {
            closeAllDropdowns();
        }
    });

    // Manejar dropdowns en móvil
    dropdownButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                const content = btn.nextElementSibling;
                const isExpanded = btn.getAttribute('aria-expanded') === 'true';
                
                // Cerrar otros dropdowns
                closeAllDropdowns(btn);

                // Toggle current dropdown
                btn.setAttribute('aria-expanded', !isExpanded);
                content.style.display = isExpanded ? 'none' : 'block';
                btn.classList.toggle('active');
            }
        });
    });

    // Cerrar menú al hacer click fuera
    document.addEventListener('click', (e) => {
        if (!navbarNav.contains(e.target) && !mobileMenu.contains(e.target) && isMenuOpen) {
            isMenuOpen = false;
            navbarNav.classList.remove('active');
            document.body.style.overflow = '';
            closeAllDropdowns();
        }
    });

    // Cerrar menú al cambiar tamaño de ventana
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            isMenuOpen = false;
            navbarNav.classList.remove('active');
            document.body.style.overflow = '';
            resetDropdowns();
        }
    });

    // Cerrar menú con tecla Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isMenuOpen) {
            isMenuOpen = false;
            navbarNav.classList.remove('active');
            document.body.style.overflow = '';
            closeAllDropdowns();
        }
    });

    // Funciones auxiliares
    function closeAllDropdowns(exceptButton = null) {
        dropdownButtons.forEach(otherBtn => {
            if (otherBtn !== exceptButton) {
                otherBtn.setAttribute('aria-expanded', 'false');
                otherBtn.classList.remove('active');
                otherBtn.nextElementSibling.style.display = 'none';
            }
        });
    }

    function resetDropdowns() {
        dropdownButtons.forEach(btn => {
            btn.setAttribute('aria-expanded', 'false');
            btn.classList.remove('active');
            btn.nextElementSibling.style.display = '';
        });
    }
});

// Tab functionality for product detail page
if (document.querySelector('.tab-btn')) {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Remove active class from all tabs and panels
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding panel
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

// Product image gallery functionality
function changeMainImage(src) {
    const mainImage = document.getElementById('mainProductImage');
    if (mainImage) {
        mainImage.src = src;
        
        // Update active state of thumbnails
        document.querySelectorAll('.thumbnail').forEach(thumb => {
            thumb.classList.remove('active');
            if (thumb.src === src) {
                thumb.classList.add('active');
            }
        });
    }
}

// Quantity selector functionality
function updateQuantity(change) {
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        let currentValue = parseInt(quantityInput.value);
        let newValue = currentValue + change;
        
        // Ensure quantity doesn't go below 1
        if (newValue < 1) newValue = 1;
        
        // Check for maximum if specified
        const max = quantityInput.getAttribute('max');
        if (max && newValue > parseInt(max)) {
            newValue = parseInt(max);
        }
        
        quantityInput.value = newValue;
    }
}
