document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Initialize toasts
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    const toastList = toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl);
    });
    
    // Show all toasts
    toastList.forEach(toast => toast.show());
    
    // Handle notification badge updates
    updateNotificationBadges();
    
    // Setup any charts
    setupCharts();
    
    // Enable form validation
    enableFormValidation();
    
    // Initialize date pickers
    initializeDatepickers();
    
    // Handle expandable/collapsible sections
    setupCollapsibles();
});

function updateNotificationBadges() {
    // Fetch notification counts and update badges
    fetch('/notifications/count')
        .then(response => response.json())
        .then(data => {
            const notificationBadge = document.getElementById('notification-badge');
            if (notificationBadge) {
                if (data.notifications > 0) {
                    notificationBadge.textContent = data.notifications;
                    notificationBadge.classList.remove('d-none');
                } else {
                    notificationBadge.textContent = '';
                    notificationBadge.classList.add('d-none');
                }
            }
            
            const messageBadge = document.getElementById('message-badge');
            if (messageBadge) {
                if (data.messages > 0) {
                    messageBadge.textContent = data.messages;
                    messageBadge.classList.remove('d-none');
                } else {
                    messageBadge.textContent = '';
                    messageBadge.classList.add('d-none');
                }
            }
        })
        .catch(error => console.error('Error updating notification badges:', error));
}

function setupCharts() {
    // Set up any Chart.js charts on the page
    const charts = document.querySelectorAll('.chart-container');
    
    charts.forEach(chartContainer => {
        const chartType = chartContainer.dataset.chartType;
        const chartId = chartContainer.dataset.chartId;
        const chartCanvas = document.getElementById(chartId);
        
        if (!chartCanvas) return;
        
        if (chartType === 'inventory') {
            setupInventoryChart(chartCanvas);
        } else if (chartType === 'donations') {
            setupDonationsChart(chartCanvas);
        } else if (chartType === 'volunteer-hours') {
            setupVolunteerHoursChart(chartCanvas);
        } else if (chartType === 'beneficiaries') {
            setupBeneficiariesChart(chartCanvas);
        }
    });
}

function enableFormValidation() {
    // Enable Bootstrap form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

function initializeDatepickers() {
    // For date/time inputs that need date pickers
    // Modern browsers have built-in date/time inputs
    const dateInputs = document.querySelectorAll('input[type="date"], input[type="datetime-local"]');
    
    dateInputs.forEach(input => {
        // Add any additional configuration if needed
        input.addEventListener('change', () => {
            validateDateRange(input);
        });
    });
}

function validateDateRange(input) {
    // Validate that dates aren't in the past if required
    if (input.dataset.noPast === 'true') {
        const selectedDate = new Date(input.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        if (selectedDate < today) {
            input.setCustomValidity('Date cannot be in the past');
        } else {
            input.setCustomValidity('');
        }
    }
}

function setupCollapsibles() {
    // Set up collapsible sections
    const collapsibles = document.querySelectorAll('.collapsible-header');
    
    collapsibles.forEach(header => {
        header.addEventListener('click', () => {
            const content = header.nextElementSibling;
            const icon = header.querySelector('.collapse-icon');
            
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
                if (icon) icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
            } else {
                content.style.maxHeight = content.scrollHeight + 'px';
                if (icon) icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
            }
        });
    });
}

// Setup notification and message loading
function loadNotifications() {
    const notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) return;
    
    fetch('/notifications')
        .then(response => response.text())
        .then(html => {
            notificationContainer.innerHTML = html;
            updateNotificationBadges();
        })
        .catch(error => console.error('Error loading notifications:', error));
}

function loadMessages() {
    const messageContainer = document.getElementById('message-container');
    if (!messageContainer) return;
    
    fetch('/messages')
        .then(response => response.text())
        .then(html => {
            messageContainer.innerHTML = html;
            updateNotificationBadges();
        })
        .catch(error => console.error('Error loading messages:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Initialize toasts
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    const toastList = toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl);
    });
    
    // Show all toasts
    toastList.forEach(toast => toast.show());
    
    // Handle notification badge updates
    updateNotificationBadges();
    
    // Setup any charts
    setupCharts();
    
    // Enable form validation
    enableFormValidation();
    
    // Initialize date pickers
    initializeDatepickers();
    
    // Handle expandable/collapsible sections
    setupCollapsibles();

    // Setup dark/light mode toggle button
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    // Load saved theme from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        htmlElement.setAttribute('data-bs-theme', savedTheme);
        if (themeToggle) {
            themeToggle.innerHTML = savedTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        }
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            themeToggle.innerHTML = newTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        });
    }
});
