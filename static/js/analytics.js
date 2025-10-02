// Postasy Analytics and Performance Monitoring

// Basic analytics tracking
class PostasyAnalytics {
    constructor() {
        this.sessionStart = Date.now();
        this.events = [];
    }

    track(event, data = {}) {
        const eventData = {
            event,
            timestamp: Date.now(),
            url: window.location.href,
            ...data
        };
        
        this.events.push(eventData);
        console.log('📊 Analytics:', eventData);
        
        // Send to backend for processing
        this.sendEvent(eventData);
    }

    sendEvent(eventData) {
        // Use sendBeacon for reliable event tracking
        if (navigator.sendBeacon) {
            navigator.sendBeacon('/api/analytics', JSON.stringify(eventData));
        } else {
            fetch('/api/analytics', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(eventData),
                keepalive: true
            }).catch(() => {}); // Silent fail
        }
    }

    trackPageView() {
        this.track('page_view', {
            title: document.title,
            referrer: document.referrer
        });
    }

    trackUserAction(action, element) {
        this.track('user_action', {
            action,
            element: element.tagName,
            text: element.textContent?.substring(0, 50)
        });
    }

    trackError(error, context = {}) {
        this.track('error', {
            message: error.message,
            stack: error.stack,
            context
        });
    }

    trackPerformance() {
        if (window.performance && window.performance.timing) {
            const timing = window.performance.timing;
            const loadTime = timing.loadEventEnd - timing.navigationStart;
            
            this.track('performance', {
                loadTime,
                domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
                firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0
            });
        }
    }
}

// Initialize analytics
const analytics = new PostasyAnalytics();

// Track page view on load
document.addEventListener('DOMContentLoaded', () => {
    analytics.trackPageView();
    analytics.trackPerformance();
});

// Track errors
window.addEventListener('error', (event) => {
    analytics.trackError(event.error || new Error(event.message), {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
    });
});

// Track unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    analytics.trackError(new Error(event.reason), {
        type: 'unhandled_promise'
    });
});

// Track user interactions
document.addEventListener('click', (event) => {
    if (event.target.matches('button, a, .btn')) {
        analytics.trackUserAction('click', event.target);
    }
});

// Track form submissions
document.addEventListener('submit', (event) => {
    analytics.trackUserAction('form_submit', event.target);
});

// Track session duration on page unload
window.addEventListener('beforeunload', () => {
    const sessionDuration = Date.now() - analytics.sessionStart;
    analytics.track('session_end', { duration: sessionDuration });
});

// Performance monitoring
class PerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.init();
    }

    init() {
        // Monitor long tasks
        if ('PerformanceObserver' in window) {
            this.observeLongTasks();
            this.observeLayoutShifts();
            this.observePaintTiming();
        }
    }

    observeLongTasks() {
        try {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.duration > 50) {
                        analytics.track('long_task', {
                            duration: entry.duration,
                            startTime: entry.startTime
                        });
                    }
                }
            });
            observer.observe({ entryTypes: ['longtask'] });
        } catch (e) {
            console.warn('Long task observation not supported');
        }
    }

    observeLayoutShifts() {
        try {
            const observer = new PerformanceObserver((list) => {
                let cumulativeScore = 0;
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) {
                        cumulativeScore += entry.value;
                    }
                }
                if (cumulativeScore > 0.1) {
                    analytics.track('layout_shift', { score: cumulativeScore });
                }
            });
            observer.observe({ entryTypes: ['layout-shift'] });
        } catch (e) {
            console.warn('Layout shift observation not supported');
        }
    }

    observePaintTiming() {
        try {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    analytics.track('paint_timing', {
                        name: entry.name,
                        startTime: entry.startTime
                    });
                }
            });
            observer.observe({ entryTypes: ['paint'] });
        } catch (e) {
            console.warn('Paint timing observation not supported');
        }
    }
}

// Initialize performance monitoring
const performanceMonitor = new PerformanceMonitor();

// Export for global access
window.PostasyAnalytics = analytics;