// API Key Management JavaScript

// Get the API base URL
const getApiBaseUrl = () => window.API_BASE_URL || window.location.origin;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is authenticated
    const token = localStorage.getItem('authToken');
    console.log('Auth token:', token ? 'Present' : 'Missing');
    
    if (token) {
        // Load API keys when page loads
        console.log('Loading API keys...');
        loadApiKeys();
    } else {
        console.log('No auth token found, user not authenticated');
        // Show no keys message if not authenticated
        const noKeysMessage = document.getElementById('noApiKeysMessage');
        const apiKeysTable = document.getElementById('apiKeysTable');
        if (noKeysMessage) noKeysMessage.style.display = 'block';
        if (apiKeysTable) apiKeysTable.style.display = 'none';
    }
});

// Function to load and display user's API keys
async function loadApiKeys() {
    console.log('loadApiKeys called');
    const loadingSpinner = document.getElementById('apiKeysLoadingSpinner');
    const errorMessage = document.getElementById('apiKeysErrorMessage');
    const tableContainer = document.getElementById('apiKeysTableContainer');
    const noKeysMessage = document.getElementById('noApiKeysMessage');
    const apiKeysTable = document.getElementById('apiKeysTable');
    
    // Show loading spinner
    if (loadingSpinner) loadingSpinner.style.display = 'block';
    if (errorMessage) errorMessage.style.display = 'none';
    if (tableContainer) tableContainer.style.display = 'none';
    
    const token = localStorage.getItem('authToken');
    console.log('Token for API call:', token ? 'Present' : 'Missing');
    console.log('Token value:', token ? token.substring(0, 20) + '...' : 'null');
    
    if (!token) {
        console.error('No authentication token found. User needs to login.');
        if (errorMessage) {
            errorMessage.textContent = 'Please login to view your API keys.';
            errorMessage.style.display = 'block';
        }
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        return;
    }
    
    try {
        const url = `${getApiBaseUrl()}/auth/api-keys`;
        console.log('Making request to:', url);
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        console.log('Response status:', response.status);
        
        if (response.status === 401) {
            console.error('Token is invalid or expired. Redirecting to login.');
            // Clear invalid token
            localStorage.removeItem('authToken');
            localStorage.removeItem('userData');
            if (errorMessage) {
                errorMessage.textContent = 'Your session has expired. Please login again.';
                errorMessage.style.display = 'block';
            }
            // Redirect to login page
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
            return;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const apiKeys = await response.json();
        
        // Hide loading spinner
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        
        if (apiKeys.length === 0) {
            // Show no keys message
            if (noKeysMessage) noKeysMessage.style.display = 'block';
            if (apiKeysTable) apiKeysTable.style.display = 'none';
        } else {
            // Show table and populate with keys
            if (tableContainer) tableContainer.style.display = 'block';
            if (noKeysMessage) noKeysMessage.style.display = 'none';
            if (apiKeysTable) apiKeysTable.style.display = 'table';
            
            populateApiKeysTable(apiKeys);
        }
    } catch (error) {
        console.error('Error loading API keys:', error);
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        if (errorMessage) {
            errorMessage.textContent = 'Failed to load API keys. Please try again.';
            errorMessage.style.display = 'block';
        }
    }
}

// Function to populate the API keys table
function populateApiKeysTable(apiKeys) {
    const tableBody = document.getElementById('apiKeysTableBody');
    if (!tableBody) return;
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Add rows for each API key
    apiKeys.forEach(key => {
        const row = document.createElement('tr');
        
        // Format dates
        const createdDate = new Date(key.created_at).toLocaleDateString();
        const lastUsedDate = key.last_used ? new Date(key.last_used).toLocaleDateString() : 'Never';
        
        // Create masked key display
        const maskedKey = key.key.substring(0, 8) + '...' + key.key.substring(key.key.length - 4);
        
        row.innerHTML = `
            <td>${escapeHtml(key.name)}</td>
            <td>
                <div class="api-key-display">
                    <span class="api-key-text" id="key-${key.id}">${maskedKey}</span>
                    <button class="copy-key-btn" onclick="copyApiKey('${key.key}', this)" title="Copy full key">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
            </td>
            <td>${createdDate}</td>
            <td>${lastUsedDate}</td>
            <td>${key.usage_count || 0}</td>
            <td>
                <span class="status-badge ${key.is_active ? 'active' : 'inactive'}">
                    ${key.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="action-button edit" onclick="openEditModal(${key.id}, '${escapeHtml(key.name)}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="action-button delete" onclick="openDeleteModal(${key.id}, '${escapeHtml(key.name)}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Function to create a new API key
async function createNewApiKey() {
    const keyNameInput = document.getElementById('newKeyName');
    const keyName = keyNameInput ? keyNameInput.value.trim() : '';
    
    if (!keyName) {
        alert('Please enter a name for your API key');
        return;
    }
    
    try {
        const response = await fetch(`${getApiBaseUrl()}/auth/api-keys`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: keyName })
        });
        
        if (!response.ok) {
            throw new Error('Failed to create API key');
        }
        
        const newKey = await response.json();
        
        // Show success message with the full key
        showApiKeyCreatedModal(newKey);
        
        // Clear the input
        if (keyNameInput) keyNameInput.value = '';
        
        // Reload the API keys table
        loadApiKeys();
    } catch (error) {
        console.error('Error creating API key:', error);
        alert('Failed to create API key. Please try again.');
    }
}

// Function to show newly created API key
function showApiKeyCreatedModal(apiKey) {
    // Create a modal to show the full API key
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'block';
    
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>API Key Created Successfully</h3>
            </div>
            <div class="modal-body">
                <p><strong>Important:</strong> Copy your API key now. You won't be able to see it again!</p>
                <div class="api-key-display" style="margin: 1rem 0;">
                    <span class="api-key-text" style="font-size: 1rem; padding: 0.5rem 1rem;">
                        ${apiKey.key}
                    </span>
                    <button class="copy-key-btn" onclick="copyApiKey('${apiKey.key}', this)">
                        <i class="fas fa-copy"></i> Copy
                    </button>
                </div>
                <p><strong>Key Name:</strong> ${escapeHtml(apiKey.name)}</p>
                <div class="modal-actions">
                    <button class="button primary" onclick="this.closest('.modal').remove()">
                        Done
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Function to copy API key to clipboard
async function copyApiKey(apiKey, button) {
    try {
        await navigator.clipboard.writeText(apiKey);
        
        // Update button to show success
        const originalContent = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i>';
        button.classList.add('copied');
        
        // Reset after 2 seconds
        setTimeout(() => {
            button.innerHTML = originalContent;
            button.classList.remove('copied');
        }, 2000);
    } catch (error) {
        console.error('Failed to copy API key:', error);
        alert('Failed to copy API key. Please copy it manually.');
    }
}

// Function to refresh API keys
function refreshApiKeys() {
    loadApiKeys();
}

// Function to open edit modal
function openEditModal(keyId, keyName) {
    const modal = document.getElementById('editApiKeyModal');
    const keyIdInput = document.getElementById('editKeyId');
    const keyNameInput = document.getElementById('editKeyName');
    
    if (modal && keyIdInput && keyNameInput) {
        keyIdInput.value = keyId;
        keyNameInput.value = keyName;
        modal.style.display = 'block';
    }
}

// Function to close edit modal
function closeEditModal() {
    const modal = document.getElementById('editApiKeyModal');
    if (modal) modal.style.display = 'none';
}

// Function to save key changes
async function saveKeyChanges() {
    const keyId = document.getElementById('editKeyId').value;
    const newName = document.getElementById('editKeyName').value.trim();
    
    if (!newName) {
        alert('Please enter a name for the API key');
        return;
    }
    
    try {
        const response = await fetch(`${getApiBaseUrl()}/auth/api-keys/${keyId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: newName })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update API key');
        }
        
        // Close modal and reload keys
        closeEditModal();
        loadApiKeys();
    } catch (error) {
        console.error('Error updating API key:', error);
        alert('Failed to update API key. Please try again.');
    }
}

// Function to open delete confirmation modal
function openDeleteModal(keyId, keyName) {
    const modal = document.getElementById('deleteConfirmModal');
    const keyIdInput = document.getElementById('deleteKeyId');
    const keyNameSpan = document.getElementById('deleteKeyName');
    
    if (modal && keyIdInput && keyNameSpan) {
        keyIdInput.value = keyId;
        keyNameSpan.textContent = keyName;
        modal.style.display = 'block';
    }
}

// Function to close delete modal
function closeDeleteModal() {
    const modal = document.getElementById('deleteConfirmModal');
    if (modal) modal.style.display = 'none';
}

// Function to confirm and delete API key
async function confirmDeleteKey() {
    const keyId = document.getElementById('deleteKeyId').value;
    
    try {
        const response = await fetch(`${getApiBaseUrl()}/auth/api-keys/${keyId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete API key');
        }
        
        // Close modal and reload keys
        closeDeleteModal();
        loadApiKeys();
    } catch (error) {
        console.error('Error deleting API key:', error);
        alert('Failed to delete API key. Please try again.');
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modals when clicking outside
window.onclick = function(event) {
    const editModal = document.getElementById('editApiKeyModal');
    const deleteModal = document.getElementById('deleteConfirmModal');
    
    if (event.target === editModal) {
        closeEditModal();
    } else if (event.target === deleteModal) {
        closeDeleteModal();
    }
};
