class NotificationSystem {
    constructor() {
        this.init();
    }

    init() {
        // Crear el contenedor de toasts si no existe
        if (!document.querySelector('.toast-container')) {
            const container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        // Crear el anunciador para lectores de pantalla
        if (!document.querySelector('.sr-announcer')) {
            const announcer = document.createElement('div');
            announcer.className = 'sr-announcer';
            announcer.setAttribute('aria-live', 'polite');
            document.body.appendChild(announcer);
        }
    }

    showToast({ type = 'info', title, message, duration = 5000 }) {
        const container = document.querySelector('.toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast--${type} animate-toast-in`;
        
        const icon = this.getIconForType(type);
        
        toast.innerHTML = `
            <span class="toast__icon" aria-hidden="true">
                <i class="${icon}"></i>
            </span>
            <div class="toast__content">
                ${title ? `<div class="toast__title">${title}</div>` : ''}
                <div class="toast__message">${message}</div>
            </div>
            <button class="toast__close" aria-label="Cerrar notificación">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Anunciar para lectores de pantalla
        const announcer = document.querySelector('.sr-announcer');
        announcer.textContent = `${type === 'error' ? 'Error' : 'Notificación'}: ${message}`;

        // Manejar el cierre
        const closeBtn = toast.querySelector('.toast__close');
        closeBtn.addEventListener('click', () => this.closeToast(toast));

        container.appendChild(toast);

        // Auto cerrar después de la duración especificada
        if (duration) {
            setTimeout(() => this.closeToast(toast), duration);
        }
    }

    closeToast(toast) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        
        setTimeout(() => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
        }, 300);
    }

    showAlert({ type = 'info', message, container, actions = [] }) {
        const alert = document.createElement('div');
        alert.className = `alert alert--${type}`;
        
        const icon = this.getIconForType(type);
        
        alert.innerHTML = `
            <span class="alert__icon" aria-hidden="true">
                <i class="${icon}"></i>
            </span>
            <div class="alert__content">${message}</div>
            ${actions.length ? '<div class="alert__actions"></div>' : ''}
        `;

        if (actions.length) {
            const actionsContainer = alert.querySelector('.alert__actions');
            actions.forEach(action => {
                const button = document.createElement('button');
                button.className = `btn btn--${action.variant || 'secondary'}`;
                button.textContent = action.text;
                button.addEventListener('click', () => {
                    action.onClick();
                    if (action.closeAfter) {
                        alert.remove();
                    }
                });
                actionsContainer.appendChild(button);
            });
        }

        const targetContainer = container ? 
            (typeof container === 'string' ? document.querySelector(container) : container) : 
            document.body;

        targetContainer.insertBefore(alert, targetContainer.firstChild);

        return {
            close: () => alert.remove()
        };
    }

    showLoading({ message = 'Cargando...' } = {}) {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div role="alert" aria-busy="true">
                <div class="loading-spinner"></div>
                <p class="mt-2 text-light">${message}</p>
            </div>
        `;
        
        document.body.appendChild(overlay);
        document.body.style.overflow = 'hidden';

        return {
            close: () => {
                overlay.remove();
                document.body.style.overflow = '';
            }
        };
    }

    getIconForType(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }
}

// Crear una instancia global
window.notifications = new NotificationSystem();

// Ejemplo de uso:
// notifications.showToast({
//     type: 'success',
//     title: 'Éxito',
//     message: 'La operación se completó correctamente'
// });

// notifications.showAlert({
//     type: 'warning',
//     message: 'Estás a punto de realizar una acción irreversible',
//     container: '#alertContainer',
//     actions: [
//         {
//             text: 'Continuar',
//             variant: 'primary',
//             onClick: () => console.log('Continuar'),
//             closeAfter: true
//         },
//         {
//             text: 'Cancelar',
//             onClick: () => console.log('Cancelar'),
//             closeAfter: true
//         }
//     ]
// });

// const loading = notifications.showLoading();
// setTimeout(() => loading.close(), 2000);