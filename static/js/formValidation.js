class FormValidator {
    constructor(form, options = {}) {
        this.form = form;
        this.options = {
            validateOnInput: true,
            validateOnBlur: true,
            ...options
        };
        this.init();
    }

    init() {
        this.form.setAttribute('novalidate', true);
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        if (this.options.validateOnInput) {
            this.form.addEventListener('input', (e) => this.handleInput(e));
        }
        
        if (this.options.validateOnBlur) {
            this.form.addEventListener('blur', (e) => this.handleBlur(e), true);
        }
    }

    handleSubmit(e) {
        if (!this.validateForm()) {
            e.preventDefault();
            this.showFormErrors();
        }
    }

    handleInput(e) {
        if (e.target.matches('input, select, textarea')) {
            this.validateField(e.target);
        }
    }

    handleBlur(e) {
        if (e.target.matches('input, select, textarea')) {
            this.validateField(e.target);
        }
    }

    validateForm() {
        let isValid = true;
        const fields = this.form.querySelectorAll('input, select, textarea');
        
        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const validations = this.getValidations(field);
        let isValid = true;
        let errorMessage = '';

        // Limpiar validaciones anteriores
        this.clearFieldValidation(field);

        // Validar requerido
        if (validations.required && !field.value.trim()) {
            isValid = false;
            errorMessage = 'Este campo es requerido';
        }

        // Validar email
        if (validations.email && !this.isValidEmail(field.value)) {
            isValid = false;
            errorMessage = 'Por favor, introduce un email válido';
        }

        // Validar longitud mínima
        if (validations.minLength && field.value.length < validations.minLength) {
            isValid = false;
            errorMessage = `Debe tener al menos ${validations.minLength} caracteres`;
        }

        // Validar longitud máxima
        if (validations.maxLength && field.value.length > validations.maxLength) {
            isValid = false;
            errorMessage = `No puede tener más de ${validations.maxLength} caracteres`;
        }

        // Validar patrón
        if (validations.pattern && !new RegExp(validations.pattern).test(field.value)) {
            isValid = false;
            errorMessage = field.dataset.patternMessage || 'El formato no es válido';
        }

        // Validar coincidencia de contraseñas
        if (validations.matches) {
            const matchElement = this.form.querySelector(`#${validations.matches}`);
            if (matchElement && field.value !== matchElement.value) {
                isValid = false;
                errorMessage = 'Las contraseñas no coinciden';
            }
        }

        // Aplicar estado de validación
        if (!isValid) {
            this.showFieldError(field, errorMessage);
        } else {
            this.showFieldSuccess(field);
        }

        return isValid;
    }

    getValidations(field) {
        return {
            required: field.hasAttribute('required'),
            email: field.type === 'email',
            minLength: field.getAttribute('minlength'),
            maxLength: field.getAttribute('maxlength'),
            pattern: field.getAttribute('pattern'),
            matches: field.dataset.matches
        };
    }

    clearFieldValidation(field) {
        field.classList.remove('is-invalid', 'is-valid');
        const container = field.closest('.form-group') || field.parentElement;
        const errorElement = container.querySelector('.form-message--error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        
        const container = field.closest('.form-group') || field.parentElement;
        const errorElement = document.createElement('div');
        errorElement.className = 'form-message form-message--error';
        errorElement.textContent = message;
        
        container.appendChild(errorElement);

        // Anunciar error para lectores de pantalla
        this.announceError(message);
    }

    showFieldSuccess(field) {
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');
    }

    showFormErrors() {
        const firstError = this.form.querySelector('.is-invalid');
        if (firstError) {
            firstError.focus();
            const errorMessage = firstError.closest('.form-group')
                .querySelector('.form-message--error')?.textContent;
            
            if (errorMessage) {
                this.announceError(errorMessage);
            }
        }
    }

    announceError(message) {
        const announcer = document.querySelector('.sr-announcer');
        if (announcer) {
            announcer.textContent = message;
        }
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    reset() {
        this.form.reset();
        const fields = this.form.querySelectorAll('input, select, textarea');
        fields.forEach(field => this.clearFieldValidation(field));
    }
}

// Ejemplo de uso:
// const form = document.querySelector('#myForm');
// const validator = new FormValidator(form, {
//     validateOnInput: true,
//     validateOnBlur: true
// });