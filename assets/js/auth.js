// Authentication and User Management JavaScript

// API Base URL - check if already defined
if (typeof API_BASE_URL === 'undefined') {
    window.API_BASE_URL = window.location.origin;
}

// Initialize authentication system
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Initializing auth system...');
    
    // Get current path
    const path = window.location.pathname;
    console.log('Current path:', path);
    
    // Setup auth tab switching
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    // Initialize forms
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
        console.log('Login form handler attached');
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
        console.log('Register form handler attached');
    }
    
    // Setup tab switching
    if (loginTab) {
        loginTab.addEventListener('click', function(e) {
            e.preventDefault();
            switchAuthTab('login');
        });
        console.log('Login tab handler attached');
    }
    
    if (registerTab) {
        registerTab.addEventListener('click', function(e) {
            e.preventDefault();
            switchAuthTab('register');
        });
        console.log('Register tab handler attached');
    }
    
    // Check if already logged in
    const token = localStorage.getItem('authToken');
    console.log('Checking stored token:', token ? 'Present' : 'Missing');
    
    if (token) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                console.log('Token is valid');
                if (path === '/' || path === '/index.html') {
                    window.location.href = '/dashboard';
                }
            } else {
                console.log('Token is invalid, clearing auth data');
                clearAuthData();
                if (path === '/dashboard' || path === '/dashboard.html') {
                    window.location.href = '/';
                }
            }
        } catch (error) {
            console.error('Error verifying token:', error);
            clearAuthData();
            if (path === '/dashboard' || path === '/dashboard.html') {
                window.location.href = '/';
            }
        }
    } else if (path === '/dashboard' || path === '/dashboard.html') {
        console.log('No token found, redirecting to login');
        window.location.href = '/';
    }
});

// Switch between login and register tabs
function switchAuthTab(tab) {
    console.log('Switching to tab:', tab);
    
    // Get all relevant elements
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (!loginTab || !registerTab) {
        console.error('Tab elements not found');
        return;
    }
    
    if (!loginForm || !registerForm) {
        console.error('Form elements not found');
        return;
    }
    
    // Update tab states
    if (tab === 'login') {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
        
        // Clear any previous messages
        const resultDiv = document.getElementById('loginResult');
        if (resultDiv) resultDiv.textContent = '';
    } else {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        registerForm.style.display = 'block';
        loginForm.style.display = 'none';
        
        // Clear any previous messages
        const resultDiv = document.getElementById('registerResult');
        if (resultDiv) resultDiv.textContent = '';
    }
    
    // Scroll to the forms section if we're on the main page
    const getStartedSection = document.getElementById('get-started');
    if (getStartedSection) {
        getStartedSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// Handle login form submission
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const resultDiv = document.getElementById('loginResult');
    
    try {
        showAuthResult(resultDiv, 'Logging in...', 'loading');
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        console.log('Login response:', {
            status: response.status,
            success: response.ok,
            has_token: !!data.access_token
        });
        
        if (response.ok && data.access_token) {
            // Store token and user data
            localStorage.setItem('authToken', data.access_token);
            localStorage.setItem('userData', JSON.stringify(data.user));
            
            showAuthResult(resultDiv, 'Login successful! Redirecting...', 'success');
            
            // Small delay to ensure token is stored
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Test token before redirect
            try {
                const testResponse = await fetch(`${API_BASE_URL}/auth/me`, {
                    headers: {
                        'Authorization': `Bearer ${data.access_token}`
                    }
                });
                
                if (testResponse.ok) {
                    console.log('Token verified successfully');
                    window.location.href = '/dashboard';
                } else {
                    console.error('Token verification failed');
                    clearAuthData();
                    showAuthResult(resultDiv, 'Authentication failed. Please try again.', 'error');
                }
            } catch (error) {
                console.error('Token verification failed:', error);
                clearAuthData();
                showAuthResult(resultDiv, 'Authentication failed. Please try again.', 'error');
            }
        } else {
            console.error('Login failed:', data);
            showAuthResult(resultDiv, data.detail || 'Login failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAuthResult(resultDiv, 'Network error. Please try again.', 'error');
    }
}

// Handle registration form submission
async function handleRegister(e) {
    e.preventDefault();
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const resultDiv = document.getElementById('registerResult');
    
    try {
        showAuthResult(resultDiv, 'Registering...', 'loading');
        
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAuthResult(resultDiv, 'Registration successful! Please log in.', 'success');
            // Switch to login tab after successful registration
            setTimeout(() => {
                switchAuthTab('login');
                // Pre-fill email for convenience
                const loginEmail = document.getElementById('loginEmail');
                if (loginEmail) loginEmail.value = email;
            }, 1500);
        } else {
            showAuthResult(resultDiv, data.detail || 'Registration failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showAuthResult(resultDiv, 'Network error. Please try again.', 'error');
    }
}

// Helper function for authenticated API requests
async function authenticatedFetch(url, options = {}) {
    const token = localStorage.getItem('authToken');
    console.log('Token for request:', token ? 'Present' : 'Missing');
    
    if (!token) {
        console.error('No auth token found');
        throw new Error('No authentication token found');
    }
    
    // Add Authorization header with Bearer prefix
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
    
    try {
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        if (response.status === 401) {
            console.error('Authentication failed');
            clearAuthData();
            window.location.href = '/';
            return response;
        }
        
        return response;
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Handle logout
function handleLogout() {
    console.log('Logging out...');
    clearAuthData();
    window.location.href = '/';
}

// Clear auth data
function clearAuthData() {
    console.log('Clearing auth data...');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
}

// Show auth result message
function showAuthResult(element, message, type) {
    if (!element) return;
    element.textContent = message;
    element.className = 'auth-result ' + type;
    
    if (type === 'loading') {
        element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + message;
    } else if (type === 'success') {
        element.innerHTML = '<i class="fas fa-check-circle"></i> ' + message;
    } else if (type === 'error') {
        element.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + message;
    }
}

// Password visibility toggle for login/register forms
function togglePassword(id) {
    const input = document.getElementById(id);
    if (input) {
        if (input.type === "password") {
            input.type = "text";
        } else {
            input.type = "password";
        }
    }
}