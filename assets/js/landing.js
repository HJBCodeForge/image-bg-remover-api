// Landing Page Authentication JavaScript

// API Base URL
const API_BASE_URL = window.location.origin;

// Authentication state
let currentUser = null;
let authToken = null;

// DOM Elements
const authModal = document.getElementById('authModal');
const authModalTitle = document.getElementById('authModalTitle');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');

// Initialize landing page
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    checkAuthStatus();
    
    // Initialize form handlers
    initializeAuthForms();
    
    // Initialize scroll animations
    initializeScrollAnimations();
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === authModal) {
            closeAuthModal();
        }
    });
});

// Check authentication status
function checkAuthStatus() {
    const token = localStorage.getItem('authToken');
    if (token) {
        authToken = token;
        // If user is already logged in, redirect to dashboard
        window.location.href = '/dashboard';
    }
}

// Show authentication modal
function showAuthModal(mode = 'login') {
    authModal.style.display = 'block';
    switchAuthMode(mode);
    
    // Focus first input
    setTimeout(() => {
        const firstInput = authModal.querySelector('form:not([style*="display: none"]) input');
        if (firstInput) firstInput.focus();
    }, 100);
}

// Close authentication modal
function closeAuthModal() {
    authModal.style.display = 'none';
    clearAuthForms();
    hideMessage();
}

// Switch between login and register modes
function switchAuthMode(mode) {
    if (mode === 'login') {
        authModalTitle.textContent = 'Login to Your Account';
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    } else if (mode === 'register') {
        authModalTitle.textContent = 'Create Your Account';
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
    }
    hideMessage();
}

// Initialize authentication forms
function initializeAuthForms() {
    // Login form handler
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        await handleLogin();
    });
    
    // Register form handler
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        await handleRegister();
    });
}

// Handle user login
async function handleLogin() {
    const formData = new FormData(loginForm);
    const loginData = {
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    try {
        showMessage('Logging in...', 'info');
        setFormLoading(loginForm, true);
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store authentication data
            localStorage.setItem('authToken', data.access_token);
            localStorage.setItem('currentUser', JSON.stringify(data.user));
            
            authToken = data.access_token;
            currentUser = data.user;
            
            showMessage('Login successful! Redirecting...', 'success');
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
        } else {
            showMessage(data.detail || 'Login failed. Please check your credentials.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage('Login failed. Please try again.', 'error');
    } finally {
        setFormLoading(loginForm, false);
    }
}

// Handle user registration
async function handleRegister() {
    const formData = new FormData(registerForm);
    const registerData = {
        name: formData.get('name'),
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    // Basic validation
    if (!registerData.name || !registerData.email || !registerData.password) {
        showMessage('Please fill in all fields.', 'error');
        return;
    }
    
    if (registerData.password.length < 6) {
        showMessage('Password must be at least 6 characters long.', 'error');
        return;
    }
    
    try {
        showMessage('Creating account...', 'info');
        setFormLoading(registerForm, true);
        
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(registerData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store authentication data
            localStorage.setItem('authToken', data.access_token);
            localStorage.setItem('currentUser', JSON.stringify(data.user));
            
            authToken = data.access_token;
            currentUser = data.user;
            
            showMessage('Account created successfully! Redirecting...', 'success');
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
        } else {
            showMessage(data.detail || 'Registration failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showMessage('Registration failed. Please try again.', 'error');
    } finally {
        setFormLoading(registerForm, false);
    }
}

// Show message in modal
function showMessage(message, type = 'info') {
    // Remove existing message
    const existingMessage = authModal.querySelector('.message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type} show`;
    messageDiv.textContent = message;
    
    // Insert at top of modal body
    const modalBody = authModal.querySelector('.modal-body');
    modalBody.insertBefore(messageDiv, modalBody.firstChild);
    
    // Auto-hide info messages
    if (type === 'info') {
        setTimeout(() => {
            hideMessage();
        }, 3000);
    }
}

// Hide message
function hideMessage() {
    const message = authModal.querySelector('.message');
    if (message) {
        message.remove();
    }
}

// Set form loading state
function setFormLoading(form, loading) {
    const submitButton = form.querySelector('button[type="submit"]');
    const inputs = form.querySelectorAll('input');
    
    if (loading) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        inputs.forEach(input => input.disabled = true);
    } else {
        submitButton.disabled = false;
        inputs.forEach(input => input.disabled = false);
        
        // Restore original button text
        if (form === loginForm) {
            submitButton.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
        } else {
            submitButton.innerHTML = '<i class="fas fa-user-plus"></i> Create Account';
        }
    }
}

// Clear authentication forms
function clearAuthForms() {
    loginForm.reset();
    registerForm.reset();
    setFormLoading(loginForm, false);
    setFormLoading(registerForm, false);
}

// Initialize scroll animations
function initializeScrollAnimations() {
    // Animate elements as they come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe sections
    const sections = document.querySelectorAll('section:not(#banner)');
    sections.forEach(section => {
        observer.observe(section);
    });
    
    // Observe cards
    const cards = document.querySelectorAll('.pricing-card, .use-case, .example-item');
    cards.forEach(card => {
        observer.observe(card);
    });
}

// Smooth scroll to sections
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Handle escape key to close modal
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && authModal.style.display === 'block') {
        closeAuthModal();
    }
});

// Add loading animation to buttons
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('button') && e.target.getAttribute('onclick')) {
        e.target.style.transform = 'scale(0.98)';
        setTimeout(() => {
            e.target.style.transform = '';
        }, 150);
    }
});

// Analytics tracking (placeholder)
function trackEvent(action, category = 'landing') {
    console.log(`Analytics: ${category} - ${action}`);
    // Add your analytics tracking code here
}

// Track button clicks
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('button')) {
        const buttonText = e.target.textContent.trim();
        trackEvent(`Button Click: ${buttonText}`);
    }
});

// Export functions for global use
window.showAuthModal = showAuthModal;
window.closeAuthModal = closeAuthModal;
window.switchAuthMode = switchAuthMode;
