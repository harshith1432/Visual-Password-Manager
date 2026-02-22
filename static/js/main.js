document.addEventListener('DOMContentLoaded', () => {
    // Theme Management
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const bodyElement = document.body;

    // Check saved theme
    const currentTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-theme', currentTheme);
    bodyElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);

    themeToggle.addEventListener('click', () => {
        const newTheme = htmlElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
        htmlElement.setAttribute('data-theme', newTheme);
        bodyElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });

    function updateThemeIcon(theme) {
        const icon = themeToggle.querySelector('i');
        if (theme === 'dark') {
            icon.classList.replace('bi-moon-stars-fill', 'bi-sun-fill');
            icon.style.color = '#fbbf24'; // Warning yellow for sun
        } else {
            icon.classList.replace('bi-sun-fill', 'bi-moon-stars-fill');
            icon.style.color = '';
        }
    }

    // Browser Notifications
    if ("Notification" in window) {
        if (Notification.permission !== 'granted' && Notification.permission !== 'denied') {
            Notification.requestPermission();
        }
    }

    // Auto-dismiss Flash Messages
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 1s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 1000);
        }, 4000);
    });
});
