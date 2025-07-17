// Authentication and User Management JavaScript

// Global variables
let currentUser = null;
let userApiKeys = [];

// API Base URL
const API_BASE_URL = 'https://web-production-faaf.up.railway.app';

// Initialize authentication system
document.addEventListener('DOMContentLoaded', function() {
    initializeAuth();
    setupAuthEventListeners();
    checkAuthState();
});

// Initialize authentication
function initializeAuth() {
    // Check for stored authentication token
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');
    
    if (token && userData) {
        try {
            currentUser = JSON.parse(userData);
            showAuthenticatedState();
        } catch (e) {
            console.error('Error parsing stored user data:', e);
            clearAuthData();
        }
    }
}

// Setup event listeners
function setupAuthEventListeners() {
    // Auth tab switching
    document.getElementById('loginTab').addEventListener('click', () => switchAuthTab('login'));
    document.getElementById('registerTab').addEventListener('click', () => switchAuthTab('register'));
    
    // Form submissions
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    
    // Dashboard actions
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);
    document.getElementById('editProfileBtn').addEventListener('click', openEditProfile);
    document.getElementById('changePasswordBtn').addEventListener('click', openChangePassword);
    
    // API Key management
    document.getElementById('createNewKeyBtn').addEventListener('click', openCreateApiKey);
    document.getElementById('refreshKeysBtn').addEventListener('click', loadUserApiKeys);
    
    // Quick actions
    document.getElementById('downloadApiDocsBtn').addEventListener('click', downloadApiDocs);
    document.getElementById('supportTicketBtn').addEventListener('click', openSupportTicket);
}

// Switch between login and register tabs
function switchAuthTab(tab) {
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (tab === 'login') {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
    } else {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        registerForm.classList.add('active');
        loginForm.classList.remove('active');
    }
    
    // Clear form results
    document.getElementById('loginResult').innerHTML = '';
    document.getElementById('registerResult').innerHTML = '';
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
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store authentication data
            localStorage.setItem('authToken', data.token);
            localStorage.setItem('userData', JSON.stringify(data.user));
            currentUser = data.user;
            
            showAuthResult(resultDiv, 'Login successful! Welcome back.', 'success');
            
            // Show authenticated state
            setTimeout(() => {
                showAuthenticatedState();
                document.getElementById('loginForm').reset();
            }, 1000);
            
        } else {
            showAuthResult(resultDiv, data.detail || 'Login failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAuthResult(resultDiv, 'Network error. Please try again.', 'error');
    }
}

// Handle register form submission
async function handleRegister(e) {
    e.preventDefault();
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const resultDiv = document.getElementById('registerResult');
    
    // Validate passwords match
    if (password !== confirmPassword) {
        showAuthResult(resultDiv, 'Passwords do not match.', 'error');
        return;
    }
    
    // Validate password strength
    if (password.length < 6) {
        showAuthResult(resultDiv, 'Password must be at least 6 characters long.', 'error');
        return;
    }
    
    try {
        showAuthResult(resultDiv, 'Creating account...', 'loading');
        
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAuthResult(resultDiv, 'Account created successfully! You can now log in.', 'success');
            
            // Switch to login tab after successful registration
            setTimeout(() => {
                switchAuthTab('login');
                document.getElementById('loginEmail').value = email;
                document.getElementById('registerForm').reset();
            }, 2000);
            
        } else {
            showAuthResult(resultDiv, data.detail || 'Registration failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showAuthResult(resultDiv, 'Network error. Please try again.', 'error');
    }
}

// Show authentication result message
function showAuthResult(element, message, type) {
    element.innerHTML = message;
    element.className = `auth-result ${type}`;
    
    if (type === 'loading') {
        element.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${message}`;
    } else if (type === 'success') {
        element.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    } else if (type === 'error') {
        element.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    }
}

// Show authenticated state
function showAuthenticatedState() {
    // Hide auth forms, show dashboard
    document.getElementById('authContainer').style.display = 'none';
    document.getElementById('userDashboard').style.display = 'block';
    
    // Show dashboard navigation
    document.getElementById('dashboardNavLink').style.display = 'block';
    
    // Update sidebar user info
    document.getElementById('userName').textContent = currentUser.name;
    document.getElementById('userEmail').textContent = currentUser.email;
    
    // Update main dashboard
    updateDashboardInfo();
    
    // Show authenticated API key section
    document.getElementById('guestApiKeySection').style.display = 'none';
    document.getElementById('authenticatedApiKeySection').style.display = 'block';
    
    // Load user's API keys
    loadUserApiKeys();
}

// Show guest state
function showGuestState() {
    // Show auth forms, hide dashboard
    document.getElementById('authContainer').style.display = 'block';
    document.getElementById('userDashboard').style.display = 'none';
    
    // Hide dashboard navigation
    document.getElementById('dashboardNavLink').style.display = 'none';
    document.getElementById('dashboard').style.display = 'none';
    
    // Show guest API key section
    document.getElementById('guestApiKeySection').style.display = 'block';
    document.getElementById('authenticatedApiKeySection').style.display = 'none';
}

// Update dashboard information
function updateDashboardInfo() {
    if (!currentUser) return;
    
    document.getElementById('dashboardUserName').textContent = currentUser.name;
    document.getElementById('dashboardUserEmail').textContent = currentUser.email;
    document.getElementById('memberSince').textContent = formatDate(currentUser.created_at);
    document.getElementById('accountStatus').textContent = currentUser.is_active ? 'Active' : 'Inactive';
    
    // Update usage statistics (these would come from API in real implementation)
    document.getElementById('apiCallsCount').textContent = currentUser.api_calls_count || '0';
    document.getElementById('totalApiKeys').textContent = userApiKeys.length;
    document.getElementById('lastActivity').textContent = currentUser.last_login ? formatDate(currentUser.last_login) : 'Never';
}

// Load user's API keys
async function loadUserApiKeys() {
    const token = localStorage.getItem('authToken');
    if (!token) return;
    
    const loadingSpinner = document.querySelector('.loading-spinner');
    const noKeysMessage = document.querySelector('.no-keys-message');
    const apiKeysTable = document.querySelector('.api-keys-table');
    
    try {
        loadingSpinner.style.display = 'block';
        noKeysMessage.style.display = 'none';
        apiKeysTable.style.display = 'none';
        
        const response = await fetch(`${API_BASE_URL}/auth/api-keys`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            userApiKeys = data.api_keys || [];
            
            loadingSpinner.style.display = 'none';
            
            if (userApiKeys.length === 0) {
                noKeysMessage.style.display = 'block';
            } else {
                displayApiKeys();
                apiKeysTable.style.display = 'table';
            }
            
            updateDashboardInfo();
        } else {
            throw new Error('Failed to load API keys');
        }
    } catch (error) {
        console.error('Error loading API keys:', error);
        loadingSpinner.style.display = 'none';
        noKeysMessage.innerHTML = '<p><i class="fas fa-exclamation-triangle"></i> Error loading API keys. Please try again.</p>';
        noKeysMessage.style.display = 'block';
    }
}

// Display API keys in table
function displayApiKeys() {
    const tbody = document.getElementById('apiKeysTableBody');
    tbody.innerHTML = '';
    
    userApiKeys.forEach(key => {
        const row = createApiKeyRow(key);
        tbody.appendChild(row);
    });
}

// Create API key table row
function createApiKeyRow(apiKey) {
    const row = document.createElement('tr');
    
    const maskedKey = apiKey.key ? `${apiKey.key.substring(0, 8)}...${apiKey.key.substring(apiKey.key.length - 4)}` : 'Hidden';
    
    row.innerHTML = `
        <td>${apiKey.name}</td>
        <td>
            <span class="api-key-display key-hidden" id="key-${apiKey.id}" data-full-key="${apiKey.key}">
                ${maskedKey}
            </span>
        </td>
        <td>${formatDate(apiKey.created_at)}</td>
        <td>${apiKey.last_used ? formatDate(apiKey.last_used) : 'Never'}</td>
        <td>${apiKey.usage_count || 0}</td>
        <td>
            <span class="status-${apiKey.is_active ? 'active' : 'inactive'}">
                ${apiKey.is_active ? 'Active' : 'Inactive'}
            </span>
        </td>
        <td>
            <div class="key-actions">
                <button class="button small" onclick="toggleKeyVisibility('${apiKey.id}')">
                    <i class="fas fa-eye"></i> Show
                </button>
                <button class="button small" onclick="copyApiKey('${apiKey.key}')">
                    <i class="fas fa-copy"></i> Copy
                </button>
                <button class="button small" onclick="deleteApiKey('${apiKey.id}')">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        </td>
    `;
    
    return row;
}

// Toggle API key visibility
function toggleKeyVisibility(keyId) {
    const keyElement = document.getElementById(`key-${keyId}`);
    const button = event.target.closest('button');
    
    if (keyElement.classList.contains('key-hidden')) {
        keyElement.textContent = keyElement.dataset.fullKey;
        keyElement.classList.remove('key-hidden');
        button.innerHTML = '<i class="fas fa-eye-slash"></i> Hide';
    } else {
        const fullKey = keyElement.dataset.fullKey;
        const maskedKey = `${fullKey.substring(0, 8)}...${fullKey.substring(fullKey.length - 4)}`;
        keyElement.textContent = maskedKey;
        keyElement.classList.add('key-hidden');
        button.innerHTML = '<i class="fas fa-eye"></i> Show';
    }
}

// Copy API key to clipboard
async function copyApiKey(key) {
    try {
        await navigator.clipboard.writeText(key);
        showNotification('API key copied to clipboard!', 'success');
    } catch (error) {
        console.error('Failed to copy API key:', error);
        showNotification('Failed to copy API key.', 'error');
    }
}

// Delete API key
async function deleteApiKey(keyId) {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
        return;
    }
    
    const token = localStorage.getItem('authToken');
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/api-keys/${keyId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            showNotification('API key deleted successfully.', 'success');
            loadUserApiKeys(); // Reload the list
        } else {
            const data = await response.json();
            showNotification(data.detail || 'Failed to delete API key.', 'error');
        }
    } catch (error) {
        console.error('Error deleting API key:', error);
        showNotification('Network error. Please try again.', 'error');
    }
}

// Handle logout
function handleLogout() {
    if (confirm('Are you sure you want to log out?')) {
        clearAuthData();
        showGuestState();
        showNotification('You have been logged out.', 'success');
    }
}

// Clear authentication data
function clearAuthData() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    currentUser = null;
    userApiKeys = [];
}

// Check authentication state
function checkAuthState() {
    if (currentUser) {
        showAuthenticatedState();
    } else {
        showGuestState();
    }
}

// Open create API key modal
function openCreateApiKey() {
    // This would open a modal in a real implementation
    const keyName = prompt('Enter a name for your new API key:');
    if (keyName) {
        createApiKey(keyName);
    }
}

// Create new API key
async function createApiKey(keyName) {
    const token = localStorage.getItem('authToken');
    
    try {
        const formData = new FormData();
        formData.append('key_name', keyName);
        
        const response = await fetch(`${API_BASE_URL}/api-keys`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            showNotification('API key created successfully!', 'success');
            loadUserApiKeys(); // Reload the list
        } else {
            const data = await response.json();
            showNotification(data.detail || 'Failed to create API key.', 'error');
        }
    } catch (error) {
        console.error('Error creating API key:', error);
        showNotification('Network error. Please try again.', 'error');
    }
}

// Open edit profile modal
function openEditProfile() {
    // This would open a modal in a real implementation
    showNotification('Profile editing feature coming soon!', 'info');
}

// Open change password modal
function openChangePassword() {
    // This would open a modal in a real implementation
    showNotification('Change password feature coming soon!', 'info');
}

// Download API documentation
function downloadApiDocs() {
    // Create and download API documentation
    const docs = generateApiDocs();
    const blob = new Blob([docs], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'background-remover-api-docs.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('API documentation downloaded!', 'success');
}

// Generate API documentation
function generateApiDocs() {
    return `# Background Remover API Documentation

## Authentication
Your API Token: ${localStorage.getItem('authToken') || 'Not logged in'}

## Base URL
${API_BASE_URL}

## Endpoints

### Generate API Key
POST /api-keys
- Requires authentication
- Parameters: key_name (string)

### Remove Background
POST /remove-background
- Parameters: file (image), api_key (string)
- Optional: alpha_matting, thresholds, etc.

### List API Keys
GET /api-keys
- Requires authentication

### Health Check
GET /health

For more details, visit the online documentation.
`;
}

// Open support ticket
function openSupportTicket() {
    // Scroll to contact form
    document.querySelector('#three').scrollIntoView({ behavior: 'smooth' });
    showNotification('Scrolled to contact form. We\'re here to help!', 'info');
}

// Show notification
function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
    `;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#6cc04a' : type === 'error' ? '#ff6347' : '#007bff'};
        color: white;
        border-radius: 0.5rem;
        z-index: 1001;
        animation: slideIn 0.3s ease;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Scroll to login (for guest users)
function scrollToLogin() {
    document.querySelector('#sidebar').scrollIntoView({ behavior: 'smooth' });
    // Focus on email input
    setTimeout(() => {
        document.getElementById('loginEmail').focus();
    }, 500);
}

// Format date helper
function formatDate(dateString) {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Override the original generateApiKey function to work with authentication
window.generateApiKey = async function() {
    if (!currentUser) {
        showNotification('Please log in to generate API keys.', 'error');
        return;
    }
    
    const keyName = document.getElementById('keyName').value;
    if (!keyName.trim()) {
        showNotification('Please enter a name for your API key.', 'error');
        return;
    }
    
    await createApiKey(keyName);
    document.getElementById('keyName').value = '';
};

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .notification {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
`;
document.head.appendChild(style);
