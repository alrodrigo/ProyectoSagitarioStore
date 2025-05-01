// Intersection Observer para carga diferida
class LazyLoader {
    constructor(options = {}) {
        this.options = {
            threshold: 0.1,
            rootMargin: '50px 0px',
            ...options
        };
        this.init();
    }

    init() {
        this.observer = new IntersectionObserver(
            (entries) => this.handleIntersection(entries),
            this.options
        );

        // Observar imágenes con data-src
        this.observeImages();
        
        // Observar videos con data-src
        this.observeVideos();
        
        // Observar iframes con data-src
        this.observeIframes();
    }

    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                this.loadElement(entry.target);
                this.observer.unobserve(entry.target);
            }
        });
    }

    loadElement(element) {
        const tagName = element.tagName.toLowerCase();
        
        switch (tagName) {
            case 'img':
                this.loadImage(element);
                break;
            case 'video':
                this.loadVideo(element);
                break;
            case 'iframe':
                this.loadIframe(element);
                break;
        }
    }

    loadImage(img) {
        const src = img.dataset.src;
        const srcset = img.dataset.srcset;
        const sizes = img.dataset.sizes;

        if (srcset) {
            img.srcset = srcset;
        }
        if (sizes) {
            img.sizes = sizes;
        }
        if (src) {
            img.src = src;
        }

        img.classList.add('loaded');
    }

    loadVideo(video) {
        const src = video.dataset.src;
        const poster = video.dataset.poster;

        if (poster) {
            video.poster = poster;
        }
        if (src) {
            video.src = src;
        }

        video.classList.add('loaded');
    }

    loadIframe(iframe) {
        const src = iframe.dataset.src;
        
        if (src) {
            iframe.src = src;
        }

        iframe.classList.add('loaded');
    }

    observeImages() {
        document.querySelectorAll('img[data-src], img[data-srcset]')
            .forEach(img => this.observer.observe(img));
    }

    observeVideos() {
        document.querySelectorAll('video[data-src]')
            .forEach(video => this.observer.observe(video));
    }

    observeIframes() {
        document.querySelectorAll('iframe[data-src]')
            .forEach(iframe => this.observer.observe(iframe));
    }
}

// Optimización de recursos
class ResourceOptimizer {
    constructor() {
        this.init();
    }

    init() {
        this.setupImageOptimization();
        this.setupResourceHints();
        this.setupFontOptimization();
    }

    setupImageOptimization() {
        // Agregar atributos de tamaño a las imágenes para evitar CLS
        document.querySelectorAll('img:not([width]):not([height])')
            .forEach(img => {
                if (img.naturalWidth && img.naturalHeight) {
                    img.setAttribute('width', img.naturalWidth);
                    img.setAttribute('height', img.naturalHeight);
                }
            });
    }

    setupResourceHints() {
        // Preconectar a dominios externos importantes
        const domains = [
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com',
            'https://cdnjs.cloudflare.com'
        ];

        domains.forEach(domain => {
            const link = document.createElement('link');
            link.rel = 'preconnect';
            link.href = domain;
            link.crossOrigin = 'anonymous';
            document.head.appendChild(link);
        });
    }

    setupFontOptimization() {
        // Detectar soporte de font-display
        const fontDisplaySupported = CSS.supports('font-display', 'swap');

        if (!fontDisplaySupported) {
            // Fallback para navegadores antiguos
            const style = document.createElement('style');
            style.textContent = `
                @font-face {
                    font-family: 'Poppins';
                    font-style: normal;
                    font-weight: 400;
                    font-display: swap;
                    src: local('Poppins Regular'), local('Poppins-Regular'),
                         url('../fonts/poppins-regular.woff2') format('woff2');
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Medición de rendimiento
class PerformanceMonitor {
    constructor() {
        this.metrics = {};
    }

    measurePageLoad() {
        if (window.performance && window.performance.timing) {
            window.addEventListener('load', () => {
                const timing = window.performance.timing;
                
                this.metrics.pageLoad = {
                    total: timing.loadEventEnd - timing.navigationStart,
                    network: timing.responseEnd - timing.fetchStart,
                    processing: timing.loadEventEnd - timing.responseEnd
                };

                this.logMetrics();
            });
        }
    }

    measureFirstPaint() {
        if (window.performance && window.performance.getEntriesByType) {
            const paint = window.performance.getEntriesByType('paint');
            const firstPaint = paint.find(entry => entry.name === 'first-paint');
            const firstContentfulPaint = paint.find(entry => entry.name === 'first-contentful-paint');

            if (firstPaint && firstContentfulPaint) {
                this.metrics.paint = {
                    firstPaint: firstPaint.startTime,
                    firstContentfulPaint: firstContentfulPaint.startTime
                };
            }
        }
    }

    measureLargestContentfulPaint() {
        if ('PerformanceObserver' in window) {
            const lcpObserver = new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                const lastEntry = entries[entries.length - 1];
                
                this.metrics.largestContentfulPaint = lastEntry.startTime;
            });

            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        }
    }

    logMetrics() {
        console.table(this.metrics);
        
        // Aquí podrías enviar las métricas a un servicio de analytics
        if (typeof gtag === 'function') {
            gtag('event', 'performance_metrics', {
                ...this.metrics
            });
        }
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    // Iniciar carga diferida
    const lazyLoader = new LazyLoader();
    
    // Optimizar recursos
    const resourceOptimizer = new ResourceOptimizer();
    
    // Monitorear rendimiento
    const performanceMonitor = new PerformanceMonitor();
    performanceMonitor.measurePageLoad();
    performanceMonitor.measureFirstPaint();
    performanceMonitor.measureLargestContentfulPaint();
});