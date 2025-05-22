document.addEventListener('DOMContentLoaded', function() {
    const notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) return;

    notificationContainer.addEventListener('click', function(event) {
        const target = event.target.closest('.dropdown-item');
        if (!target) return;

        // Send POST request to mark notifications as read
        fetch('/notifications/mark_read', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update notification badge
                const notificationBadge = document.getElementById('notification-badge');
                if (notificationBadge) {
                    notificationBadge.textContent = '';
                    notificationBadge.classList.add('d-none');
                }
            }
        })
        .catch(error => console.error('Error marking notifications as read:', error));
    });

    // Helper function to get CSRF token from meta tag
    function getCookie(name) {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : null;
    }
});
