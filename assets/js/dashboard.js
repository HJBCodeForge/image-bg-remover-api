// Dashboard JavaScript

// API Base URL
const API_BASE_URL = window.location.origin;

// Authentication state
let currentUser = null;
let authToken = null;
let userApiKeys = [];

// DOM Elements
const createKeyModal = document.getElementById('createKeyModal');
const keyDetailsModal = document.getElementById('keyDetailsModal');
const createKeyForm = document.getElementById('createKeyForm');
const imageInput = document.getElementById('imageInput');
const uploadArea = document.getElementById('uploadArea');

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    checkAuthStatus();
    
    // Initialize dashboard if authenticated
    if (authToken) {
        initializeDashboard();
    }
});

// Check authentication status
function checkAuthStatus() {
    authToken = localStorage.getItem('authToken');
    const userString = localStorage.getItem('currentUser');
    
    if (!authToken || !userString) {
        // Redirect to landing page if not authenticated
        window.location.href = '/';
        return;
    }
    
    try {
        currentUser = JSON.parse(userString);
    } catch (error) {
        console.error('Failed to parse user data:', error);
        logout();
        return;
    }
}

// Initialize dashboard
async function initializeDashboard() {
    // Load user profile
    await loadUserProfile();
    
    // Load API keys
    await loadApiKeys();
    
    // Initialize file upload
    initializeFileUpload();
    
    // Initialize forms
    initializeForms();
    
    // Update statistics
    updateStatistics();
}

// Load user profile
async function loadUserProfile() {
    try {
        // Update UI with stored user data first
        updateProfileUI(currentUser);
        
        // Fetch fresh user data
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const userData = await response.json();
            currentUser = userData;
            localStorage.setItem('currentUser', JSON.stringify(userData));
            updateProfileUI(userData);
        } else if (response.status === 401) {
            logout();
        }
    } catch (error) {
        console.error('Failed to load user profile:', error);
    }
}

// Update profile UI
function updateProfileUI(user) {
    document.getElementById('userName').textContent = user.name;
    document.getElementById('profileName').textContent = user.name;
    document.getElementById('profileEmail').textContent = user.email;
    document.getElementById('profileCreated').textContent = formatDate(user.created_at);
    document.getElementById('profileLastLogin').textContent = user.last_login ? formatDate(user.last_login) : 'Never';
    document.getElementById('profileApiCalls').textContent = user.api_calls_count || 0;
}

// Load API keys
async function loadApiKeys() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/api-keys`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            userApiKeys = await response.json();
            displayApiKeys(userApiKeys);
        } else if (response.status === 401) {
            logout();
        } else {
            throw new Error('Failed to load API keys');
        }
    } catch (error) {
        console.error('Failed to load API keys:', error);
        document.getElementById('apiKeysContainer').innerHTML = 
            '<div class="error">Failed to load API keys. Please refresh the page.</div>';
    }
}

// Display API keys
function displayApiKeys(apiKeys) {
    const container = document.getElementById('apiKeysContainer');
    
    if (apiKeys.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-key"></i>
                <h3>No API Keys</h3>
                <p>Create your first API key to start using the background removal service.</p>
                <button class="button primary" onclick="showCreateKeyModal()">
                    <i class="fas fa-plus"></i> Create API Key
                </button>
            </div>
        `;
        return;
    }
    
    const apiKeysHtml = apiKeys.map(key => `
        <div class="api-key-item">
            <div class="key-info">
                <div class="key-name">
                    <i class="fas fa-key"></i>
                    <strong>${escapeHtml(key.name)}</strong>
                </div>
                <div class="key-details">
                    <span class="key-partial">${key.key.substring(0, 8)}...${key.key.substring(key.key.length - 4)}</span>
                    <span class="key-created">Created: ${formatDate(key.created_at)}</span>
                    <span class="key-usage">Used: ${key.usage_count} times</span>
                    ${key.last_used ? `<span class="key-last-used">Last used: ${formatDate(key.last_used)}</span>` : ''}
                </div>
            </div>
            <div class="key-actions">
                <button class="button small" onclick="copyApiKey('${key.key}')">
                    <i class="fas fa-copy"></i> Copy
                </button>
                <button class="button small secondary" onclick="deleteApiKey(${key.id}, '${escapeHtml(key.name)}')">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = apiKeysHtml;
}

// Show create API key modal
function showCreateKeyModal() {
    createKeyModal.style.display = 'block';
    document.getElementById('keyName').focus();
}

// Close create API key modal
function closeCreateKeyModal() {
    createKeyModal.style.display = 'none';
    createKeyForm.reset();
}

// Close API key details modal
function closeKeyDetailsModal() {
    keyDetailsModal.style.display = 'none';
}

// Initialize forms
function initializeForms() {
    createKeyForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        await handleCreateApiKey();
    });
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === createKeyModal) {
            closeCreateKeyModal();
        }
        if (event.target === keyDetailsModal) {
            closeKeyDetailsModal();
        }
    });
}

// Handle create API key
async function handleCreateApiKey() {
    const formData = new FormData(createKeyForm);
    const keyData = {
        name: formData.get('name')
    };
    
    try {
        const submitButton = createKeyForm.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
        submitButton.disabled = true;
        
        const response = await fetch(`${API_BASE_URL}/auth/api-keys`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(keyData)
        });
        
        if (response.ok) {
            const newKey = await response.json();
            
            // Show the new API key
            document.getElementById('newApiKey').value = newKey.key;
            closeCreateKeyModal();
            keyDetailsModal.style.display = 'block';
            
            // Reload API keys
            await loadApiKeys();
            updateStatistics();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to create API key');
        }
    } catch (error) {
        console.error('Failed to create API key:', error);
        alert('Failed to create API key. Please try again.');
    } finally {
        const submitButton = createKeyForm.querySelector('button[type="submit"]');
        submitButton.innerHTML = '<i class="fas fa-key"></i> Create API Key';
        submitButton.disabled = false;
    }
}

// Copy API key to clipboard
async function copyApiKey(apiKey) {
    try {
        if (apiKey) {
            await navigator.clipboard.writeText(apiKey);
        } else {
            const keyInput = document.getElementById('newApiKey');
            await navigator.clipboard.writeText(keyInput.value);
            keyInput.select();
        }
        
        // Show feedback
        showNotification('API key copied to clipboard!', 'success');
    } catch (error) {
        console.error('Failed to copy API key:', error);
        // Fallback for older browsers
        const keyInput = document.getElementById('newApiKey');
        keyInput.select();
        document.execCommand('copy');
        showNotification('API key copied to clipboard!', 'success');
    }
}

// Delete API key
async function deleteApiKey(keyId, keyName) {
    if (!confirm(`Are you sure you want to delete the API key "${keyName}"? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/api-keys/${keyId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            showNotification('API key deleted successfully', 'success');
            await loadApiKeys();
            updateStatistics();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to delete API key');
        }
    } catch (error) {
        console.error('Failed to delete API key:', error);
        alert('Failed to delete API key. Please try again.');
    }
}

// Update statistics
function updateStatistics() {
    document.getElementById('totalKeys').textContent = userApiKeys.length;
    
    // Calculate total usage
    const totalUsage = userApiKeys.reduce((sum, key) => sum + (key.usage_count || 0), 0);
    document.getElementById('totalImages').textContent = totalUsage;
    
    // Find last used
    const lastUsedTimes = userApiKeys
        .filter(key => key.last_used)
        .map(key => new Date(key.last_used))
        .sort((a, b) => b - a);
    
    if (lastUsedTimes.length > 0) {
        document.getElementById('lastUsed').textContent = formatDate(lastUsedTimes[0]);
    } else {
        document.getElementById('lastUsed').textContent = 'Never';
    }
}

// Initialize file upload
function initializeFileUpload() {
    // Drag and drop handlers
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleImageUpload(files[0]);
        }
    });
    
    // File input handler
    imageInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleImageUpload(e.target.files[0]);
        }
    });
}

// Handle image upload and processing
async function handleImageUpload(file) {
    // Validate file type
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }
    
    // Check if user has API keys
    if (userApiKeys.length === 0) {
        alert('You need to create an API key first to use the background removal service.');
        showCreateKeyModal();
        return;
    }
    
    // Show processing state
    document.getElementById('uploadArea').style.display = 'none';
    document.getElementById('imageProcessing').style.display = 'block';
    document.getElementById('imageResult').style.display = 'none';
    
    try {
        // Use the first available API key
        const apiKey = userApiKeys[0].key;
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('api_key', apiKey);
        formData.append('alpha_matting', 'false');
        
        // Process image
        const response = await fetch(`${API_BASE_URL}/remove-background`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            // Show original image
            const originalImage = document.getElementById('originalImage');
            originalImage.src = URL.createObjectURL(file);
            
            // Show processed image
            const processedImage = document.getElementById('processedImage');
            const blob = await response.blob();
            processedImage.src = URL.createObjectURL(blob);
            processedImage.dataset.blob = URL.createObjectURL(blob);
            
            // Show result
            document.getElementById('imageProcessing').style.display = 'none';
            document.getElementById('imageResult').style.display = 'block';
            
            // Reload API keys to update usage count
            await loadApiKeys();
            updateStatistics();
        } else {
            throw new Error('Failed to process image');
        }
    } catch (error) {
        console.error('Failed to process image:', error);
        alert('Failed to process image. Please try again.');
        resetDemo();
    }
}

// Download processed image
function downloadImage() {
    const processedImage = document.getElementById('processedImage');
    const blobUrl = processedImage.dataset.blob;
    
    if (blobUrl) {
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = 'background_removed.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Reset demo
function resetDemo() {
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('imageProcessing').style.display = 'none';
    document.getElementById('imageResult').style.display = 'none';
    imageInput.value = '';
}

// Show documentation
function showDocumentation() {
    // You can implement this to show API documentation
    alert('API Documentation will be available soon!');
}

// Scroll to section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// Logout function
function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    window.location.href = '/';
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Show with animation
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Remove after delay
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
