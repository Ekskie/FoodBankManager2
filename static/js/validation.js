document.addEventListener('DOMContentLoaded', function() {
    // Get all forms with the 'needs-validation' class
    const forms = document.querySelectorAll('.needs-validation');
    
    // Apply custom validation to each form
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            // Check if the form is valid
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            // Apply custom validation for specific form types
            if (form.id === 'registration-form') {
                validateRegistrationForm(form, event);
            } else if (form.id === 'donation-form') {
                validateDonationForm(form, event);
            } else if (form.id === 'food-request-form') {
                validateFoodRequestForm(form, event);
            } else if (form.id === 'volunteer-form') {
                validateVolunteerForm(form, event);
            } else if (form.id === 'password-form') {
                validatePasswordForm(form, event);
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Add event listeners for real-time validation
    setupRealTimeValidation();
});

function setupRealTimeValidation() {
    // Password strength validation
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        if (input.id.includes('password')) {
            input.addEventListener('input', function() {
                validatePasswordStrength(input);
            });
        }
    });
    
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateEmail(input);
        });
    });
    
    // Phone number validation
    const phoneInputs = document.querySelectorAll('input[id*="phone"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            validatePhone(input);
        });
    });
    
    // Date validation
    const dateInputs = document.querySelectorAll('input[type="date"], input[type="datetime-local"]');
    dateInputs.forEach(input => {
        input.addEventListener('change', function() {
            validateDate(input);
        });
    });
    
    // Numeric input validation
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateNumber(input);
        });
    });
}

// Registration form validation
function validateRegistrationForm(form, event) {
    const password = form.querySelector('#password');
    const confirmPassword = form.querySelector('#password2');
    
    // Check if passwords match
    if (password && confirmPassword && password.value !== confirmPassword.value) {
        confirmPassword.setCustomValidity('Passwords must match');
        event.preventDefault();
        event.stopPropagation();
    } else if (confirmPassword) {
        confirmPassword.setCustomValidity('');
    }
    
    // Check password strength
    if (password && password.value.length < 8) {
        password.setCustomValidity('Password must be at least 8 characters long');
        event.preventDefault();
        event.stopPropagation();
    } else if (password) {
        password.setCustomValidity('');
    }
}

// Donation form validation
function validateDonationForm(form, event) {
    const donationType = form.querySelector('#donation_type');
    const amount = form.querySelector('#amount');
    
    // If donation type is monetary, amount is required
    if (donationType && amount && donationType.value === 'money') {
        if (!amount.value || parseFloat(amount.value) <= 0) {
            amount.setCustomValidity('Please enter a valid donation amount');
            event.preventDefault();
            event.stopPropagation();
        } else {
            amount.setCustomValidity('');
        }
    } else if (amount) {
        amount.setCustomValidity('');
    }
}

// Food request form validation
function validateFoodRequestForm(form, event) {
    const householdSize = form.querySelector('#household_size');
    const requestItems = form.querySelector('#request_items');
    
    // Validate household size
    if (householdSize && (isNaN(householdSize.value) || parseInt(householdSize.value) <= 0)) {
        householdSize.setCustomValidity('Please enter a valid household size');
        event.preventDefault();
        event.stopPropagation();
    } else if (householdSize) {
        householdSize.setCustomValidity('');
    }
    
    // Validate requested items
    if (requestItems && requestItems.value.trim() === '') {
        requestItems.setCustomValidity('Please specify what items you need');
        event.preventDefault();
        event.stopPropagation();
    } else if (requestItems) {
        requestItems.setCustomValidity('');
    }
}

// Volunteer form validation
function validateVolunteerForm(form, event) {
    const date = form.querySelector('#date');
    const startTime = form.querySelector('#start_time');
    const endTime = form.querySelector('#end_time');
    
    // Check if end time is after start time
    if (startTime && endTime) {
        const startVal = startTime.value;
        const endVal = endTime.value;
        
        if (startVal && endVal && startVal >= endVal) {
            endTime.setCustomValidity('End time must be after start time');
            event.preventDefault();
            event.stopPropagation();
        } else {
            endTime.setCustomValidity('');
        }
    }
    
    // Check if date is in the past
    if (date) {
        const selectedDate = new Date(date.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        if (selectedDate < today) {
            date.setCustomValidity('Date cannot be in the past');
            event.preventDefault();
            event.stopPropagation();
        } else {
            date.setCustomValidity('');
        }
    }
}

// Password change form validation
function validatePasswordForm(form, event) {
    const currentPassword = form.querySelector('#current_password');
    const newPassword = form.querySelector('#new_password');
    const confirmPassword = form.querySelector('#confirm_password');
    
    // Check if new password is different from current
    if (currentPassword && newPassword && currentPassword.value === newPassword.value) {
        newPassword.setCustomValidity('New password must be different from current password');
        event.preventDefault();
        event.stopPropagation();
    } else if (newPassword) {
        newPassword.setCustomValidity('');
    }
    
    // Check if passwords match
    if (newPassword && confirmPassword && newPassword.value !== confirmPassword.value) {
        confirmPassword.setCustomValidity('Passwords must match');
        event.preventDefault();
        event.stopPropagation();
    } else if (confirmPassword) {
        confirmPassword.setCustomValidity('');
    }
    
    // Check password strength
    if (newPassword && newPassword.value.length < 8) {
        newPassword.setCustomValidity('Password must be at least 8 characters long');
        event.preventDefault();
        event.stopPropagation();
    } else if (newPassword) {
        newPassword.setCustomValidity('');
    }
}

// Validate password strength
function validatePasswordStrength(input) {
    const password = input.value;
    const strengthBar = document.getElementById(`${input.id}-strength`);
    
    if (!strengthBar) return;
    
    // Clear custom validity
    input.setCustomValidity('');
    
    // Check password strength
    let strength = 0;
    
    // Length check
    if (password.length >= 8) strength += 1;
    if (password.length >= 12) strength += 1;
    
    // Character checks
    if (/[A-Z]/.test(password)) strength += 1; // Has uppercase
    if (/[a-z]/.test(password)) strength += 1; // Has lowercase
    if (/[0-9]/.test(password)) strength += 1; // Has number
    if (/[^A-Za-z0-9]/.test(password)) strength += 1; // Has special char
    
    // Update strength bar
    strengthBar.style.width = `${Math.min(100, (strength / 6) * 100)}%`;
    
    // Update color based on strength
    if (strength < 3) {
        strengthBar.className = 'progress-bar bg-danger';
        strengthBar.textContent = 'Weak';
        if (password.length > 0) input.setCustomValidity('Password is too weak');
    } else if (strength < 5) {
        strengthBar.className = 'progress-bar bg-warning';
        strengthBar.textContent = 'Medium';
        input.setCustomValidity('');
    } else {
        strengthBar.className = 'progress-bar bg-success';
        strengthBar.textContent = 'Strong';
        input.setCustomValidity('');
    }
}

// Validate email format
function validateEmail(input) {
    const email = input.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        input.setCustomValidity('Please enter a valid email address');
    } else {
        input.setCustomValidity('');
    }
}

// Validate phone format
function validatePhone(input) {
    const phone = input.value.replace(/\D/g, ''); // Remove non-digits
    
    if (phone && phone.length < 10) {
        input.setCustomValidity('Please enter a valid phone number');
    } else {
        input.setCustomValidity('');
    }
    
    // Format phone number as user types
    if (phone.length > 0) {
        let formattedPhone = '';
        
        if (phone.length > 0) {
            formattedPhone = '(' + phone.substring(0, Math.min(3, phone.length));
            
            if (phone.length >= 4) {
                formattedPhone += ') ' + phone.substring(3, Math.min(6, phone.length));
            }
            
            if (phone.length >= 7) {
                formattedPhone += '-' + phone.substring(6, Math.min(10, phone.length));
            }
        }
        
        if (input.value !== formattedPhone && !input.readOnly) {
            input.value = formattedPhone;
        }
    }
}

// Validate date inputs
function validateDate(input) {
    const selectedDate = new Date(input.value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    // Check if date should not be in the past (based on data-no-past attribute)
    if (input.dataset.noPast === 'true' && selectedDate < today) {
        input.setCustomValidity('Date cannot be in the past');
    } else {
        input.setCustomValidity('');
    }
}

// Validate numeric inputs
function validateNumber(input) {
    const value = parseFloat(input.value);
    const min = parseFloat(input.min);
    const max = parseFloat(input.max);
    
    if (isNaN(value)) {
        input.setCustomValidity('Please enter a number');
    } else if (!isNaN(min) && value < min) {
        input.setCustomValidity(`Value cannot be less than ${min}`);
    } else if (!isNaN(max) && value > max) {
        input.setCustomValidity(`Value cannot be greater than ${max}`);
    } else {
        input.setCustomValidity('');
    }
}
