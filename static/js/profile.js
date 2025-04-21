document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const navItems = document.querySelectorAll('.profile-nav .nav-item');
    const tabPanels = document.querySelectorAll('.tab-panel');

    function switchTab(tabId) {
        // Update navigation items
        navItems.forEach(item => {
            if (item.getAttribute('href') === `#${tabId}`) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // Update tab panels
        tabPanels.forEach(panel => {
            if (panel.id === tabId) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });

        // Update URL hash without scrolling
        history.pushState(null, null, `#${tabId}`);
    }

    // Handle tab navigation
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const tabId = this.getAttribute('href').substring(1);
            switchTab(tabId);
        });
    });

    // Handle direct URL access with hash
    if (window.location.hash) {
        const tabId = window.location.hash.substring(1);
        switchTab(tabId);
    }

    // Personal Information editing
    const editInfoBtn = document.getElementById('edit-info');
    const cancelEditBtn = document.getElementById('cancel-edit');
    const infoForm = document.getElementById('info-form');
    const formInputs = infoForm.querySelectorAll('input');
    const formActions = infoForm.querySelector('.form-actions');

    if (editInfoBtn) {
        editInfoBtn.addEventListener('click', function() {
            formInputs.forEach(input => {
                input.disabled = false;
            });
            formActions.style.display = 'flex';
            this.style.display = 'none';
        });
    }

    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', function() {
            formInputs.forEach(input => {
                input.disabled = true;
                // Reset to original value
                const originalValue = input.defaultValue;
                input.value = originalValue;
            });
            formActions.style.display = 'none';
            editInfoBtn.style.display = 'block';
        });
    }

    // Address management
    const addAddressBtn = document.getElementById('add-address');
    const addFirstAddressBtn = document.getElementById('add-first-address');
    
    function showAddressModal(isEdit = false, addressData = null) {
        // Implementation for address modal will be added later
        console.log('Show address modal', { isEdit, addressData });
    }

    if (addAddressBtn) {
        addAddressBtn.addEventListener('click', () => showAddressModal());
    }

    if (addFirstAddressBtn) {
        addFirstAddressBtn.addEventListener('click', () => showAddressModal());
    }

    // Handle address actions
    document.querySelectorAll('.address-card .btn-edit').forEach(btn => {
        btn.addEventListener('click', function() {
            const addressId = this.dataset.id;
            // Fetch address data and show modal
            fetch(`/api/addresses/${addressId}/`)
                .then(response => response.json())
                .then(data => showAddressModal(true, data))
                .catch(error => console.error('Error:', error));
        });
    });

    document.querySelectorAll('.address-card .btn-delete').forEach(btn => {
        btn.addEventListener('click', function() {
            if (confirm('¿Estás seguro de que deseas eliminar esta dirección?')) {
                const addressId = this.dataset.id;
                fetch(`/api/addresses/${addressId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => {
                    if (response.ok) {
                        // Remove the address card from the DOM
                        this.closest('.address-card').remove();
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    });

    document.querySelectorAll('.address-card .btn-default').forEach(btn => {
        btn.addEventListener('click', function() {
            const addressId = this.dataset.id;
            fetch(`/api/addresses/${addressId}/set-default/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => {
                if (response.ok) {
                    // Reload the page to reflect changes
                    window.location.reload();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Password visibility toggle
    const toggleButtons = document.querySelectorAll('.toggle-password');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');

            if (input.type === 'password') {
                input.type = 'text';
                icon.className = 'far fa-eye-slash';
            } else {
                input.type = 'password';
                icon.className = 'far fa-eye';
            }
        });
    });

    // Password validation
    const passwordForm = document.querySelector('.password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            const newPassword1 = this.querySelector('#new_password1').value;
            const newPassword2 = this.querySelector('#new_password2').value;

            if (newPassword1 !== newPassword2) {
                e.preventDefault();
                alert('Las contraseñas no coinciden');
            }
        });
    }

    // Preferences form autosave
    const preferencesForm = document.querySelector('.preferences-form');
    if (preferencesForm) {
        const checkboxes = preferencesForm.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const formData = new FormData(preferencesForm);
                fetch('/api/preferences/update/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Show a brief success message
                        const message = document.createElement('div');
                        message.className = 'alert alert-success fade-out';
                        message.textContent = 'Preferencias guardadas';
                        preferencesForm.insertBefore(message, preferencesForm.firstChild);
                        
                        // Remove the message after 3 seconds
                        setTimeout(() => message.remove(), 3000);
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        });
    }
});