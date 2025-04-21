document.addEventListener('DOMContentLoaded', function() {
    // Manejo de mostrar/ocultar contraseña
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    const toggleButtons = document.querySelectorAll('.toggle-password');

    toggleButtons.forEach((button, index) => {
        button.addEventListener('click', function() {
            const input = passwordInputs[index];
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

    // Validación del formulario
    const form = document.querySelector('.auth-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const emailInput = document.getElementById('email');
            const passwordInput = document.getElementById('password');
            let isValid = true;

            // Validar email
            if (!isValidEmail(emailInput.value)) {
                showError(emailInput, 'Por favor ingresa un correo electrónico válido');
                isValid = false;
            } else {
                removeError(emailInput);
            }

            // Validar contraseña
            if (passwordInput.value.length < 8) {
                showError(passwordInput, 'La contraseña debe tener al menos 8 caracteres');
                isValid = false;
            } else {
                removeError(passwordInput);
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // Funciones auxiliares
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function showError(input, message) {
        const formGroup = input.closest('.form-group');
        let errorDiv = formGroup.querySelector('.error-message');
        
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            formGroup.appendChild(errorDiv);
        }
        
        errorDiv.textContent = message;
        input.classList.add('error');
    }

    function removeError(input) {
        const formGroup = input.closest('.form-group');
        const errorDiv = formGroup.querySelector('.error-message');
        
        if (errorDiv) {
            errorDiv.remove();
        }
        input.classList.remove('error');
    }

    // Inicializar botones de redes sociales
    const googleBtn = document.querySelector('.btn-google');
    const facebookBtn = document.querySelector('.btn-facebook');

    if (googleBtn) {
        googleBtn.addEventListener('click', function() {
            window.location.href = '/auth/google/login/';
        });
    }

    if (facebookBtn) {
        facebookBtn.addEventListener('click', function() {
            window.location.href = '/auth/facebook/login/';
        });
    }

    // Password validation for registration
    const password1Input = document.getElementById('password1');
    const password2Input = document.getElementById('password2');
    
    if (password1Input) {
        const requirements = {
            length: { regex: /.{8,}/, element: document.getElementById('length') },
            uppercase: { regex: /[A-Z]/, element: document.getElementById('uppercase') },
            lowercase: { regex: /[a-z]/, element: document.getElementById('lowercase') },
            number: { regex: /[0-9]/, element: document.getElementById('number') }
        };

        password1Input.addEventListener('input', function() {
            const password = this.value;
            
            // Check each requirement
            Object.keys(requirements).forEach(req => {
                const { regex, element } = requirements[req];
                if (element) {
                    if (regex.test(password)) {
                        element.classList.add('valid');
                        element.classList.remove('invalid');
                    } else {
                        element.classList.add('invalid');
                        element.classList.remove('valid');
                    }
                }
            });
        });

        // Validate password match
        if (password2Input) {
            password2Input.addEventListener('input', function() {
                if (this.value === password1Input.value) {
                    removeError(this);
                } else {
                    showError(this, 'Las contraseñas no coinciden');
                }
            });
        }
    }

    // Social login handlers
    function handleSocialLogin(provider) {
        // Save current URL to redirect back after login
        sessionStorage.setItem('redirectUrl', window.location.href);
        window.location.href = `/auth/${provider}/login/`;
    }

    const googleBtn = document.querySelector('.btn-google');
    if (googleBtn) {
        googleBtn.addEventListener('click', () => handleSocialLogin('google'));
    }

    const facebookBtn = document.querySelector('.btn-facebook');
    if (facebookBtn) {
        facebookBtn.addEventListener('click', () => handleSocialLogin('facebook'));
    }

    // Form submission handler
    const form = document.querySelector('.auth-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;

            // Reset previous errors
            const inputs = form.querySelectorAll('input');
            inputs.forEach(input => removeError(input));

            // Email validation
            const emailInput = form.querySelector('input[type="email"]');
            if (emailInput && !isValidEmail(emailInput.value)) {
                showError(emailInput, 'Por favor ingresa un correo electrónico válido');
                isValid = false;
            }

            // Password validation for registration
            if (password1Input && password2Input) {
                const password = password1Input.value;
                
                // Check password requirements
                const requirements = {
                    length: /.{8,}/,
                    uppercase: /[A-Z]/,
                    lowercase: /[a-z]/,
                    number: /[0-9]/
                };

                Object.entries(requirements).forEach(([key, regex]) => {
                    if (!regex.test(password)) {
                        isValid = false;
                        showError(password1Input, 'La contraseña no cumple con los requisitos mínimos');
                    }
                });

                // Check passwords match
                if (password1Input.value !== password2Input.value) {
                    showError(password2Input, 'Las contraseñas no coinciden');
                    isValid = false;
                }
            }

            // Terms validation for registration
            const termsCheckbox = document.getElementById('terms');
            if (termsCheckbox && !termsCheckbox.checked) {
                showError(termsCheckbox, 'Debes aceptar los términos y condiciones');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }
});