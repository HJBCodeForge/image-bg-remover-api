// Background Remover API Demo JavaScript
// Configuration and API interaction functionality

// Configuration - Auto-detect API URL
function getApiUrl() {
	// Check if we're running locally
	if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
		return 'http://localhost:8000';
	}
	// Production URL
	return 'https://web-production-faaf.up.railway.app';
}

const API_BASE_URL = getApiUrl();
console.log('API_BASE_URL:', API_BASE_URL);

// Check if API is properly configured
function checkApiConfiguration() {
	if (API_BASE_URL.includes('your-api-name')) {
		const warningDiv = document.createElement('div');
		warningDiv.className = 'demo-result error';
		warningDiv.style.margin = '20px 0';
		warningDiv.innerHTML = `
			<strong>⚠️ API Configuration Required</strong><br>
			The API URL needs to be configured. Please:<br>
			1. Deploy the API to Railway (see DEPLOYMENT_GUIDE.md)<br>
			2. Update the API_BASE_URL in this file<br>
			3. Or run locally with: <code>python3 main.py</code>
		`;
		document.querySelector('.demo-container').insertBefore(warningDiv, document.querySelector('.demo-section'));
		
		// Disable buttons
		document.querySelectorAll('.button').forEach(btn => {
			btn.disabled = true;
			btn.style.opacity = '0.5';
		});
	}
}

// API Key Generation
async function generateApiKey() {
	const keyName = document.getElementById('keyName').value;
	const resultDiv = document.getElementById('apiKeyResult');
	
	if (!keyName.trim()) {
		resultDiv.innerHTML = '<div class="demo-result error">Please enter a name for your API key</div>';
		return;
	}
	
	// Check if API is configured
	if (API_BASE_URL.includes('your-api-name')) {
		resultDiv.innerHTML = `
			<div class="demo-result error">
				<strong>⚠️ API Not Configured</strong><br>
				Please deploy the API first or run it locally.<br>
				See <strong>DEPLOYMENT_GUIDE.md</strong> for instructions.
			</div>
		`;
		return;
	}
	
	try {
		// Use form data instead of JSON as the API expects form data
		const formData = new FormData();
		formData.append('key_name', keyName);
		
		const response = await fetch(`${API_BASE_URL}/api-keys`, {
			method: 'POST',
			body: formData
		});
		
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		
		const data = await response.json();
		
		// Auto-fill the API key input
		document.getElementById('apiKeyInput').value = data.key;
		
		resultDiv.innerHTML = `
			<div class="demo-result success">
				<strong>✓ API Key Generated Successfully!</strong>
				<div class="api-key-display">
					<strong>Key:</strong> ${data.key}<br>
					<strong>Name:</strong> ${data.name}<br>
					<strong>Status:</strong> ${data.is_active ? 'active' : 'inactive'}<br>
					<strong>Created:</strong> ${data.created_at}
				</div>
				<p><small>💡 Your API key has been automatically filled in the form below</small></p>
			</div>
		`;
		
	} catch (error) {
		let errorMessage = error.message;
		
		// Provide more specific error messages
		if (error.message.includes('Failed to fetch') || error.name === 'TypeError') {
			errorMessage = `
				<strong>Connection Failed</strong><br>
				Cannot connect to the API server at:<br>
				<code>${API_BASE_URL}</code><br><br>
				<strong>Possible solutions:</strong><br>
				• Make sure the API is running locally: <code>python3 main.py</code><br>
				• Deploy the API to Railway (see DEPLOYMENT_GUIDE.md)<br>
				• Check if the API URL is correct
			`;
		}
		
		resultDiv.innerHTML = `<div class="demo-result error">✖ ${errorMessage}</div>`;
	}
}

// Background Removal Function
async function removeBackground() {
	const apiKey = document.getElementById('apiKeyInput').value;
	const fileInput = document.getElementById('imageFile');
	const resultDiv = document.getElementById('imageResult');
	
	if (!apiKey.trim()) {
		resultDiv.innerHTML = '<div class="demo-result error">Please enter your API key</div>';
		return;
	}
	
	if (!fileInput.files || fileInput.files.length === 0) {
		resultDiv.innerHTML = '<div class="demo-result error">Please select an image file</div>';
		return;
	}
	
	const file = fileInput.files[0];
	
	// Validate file type
	const supportedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp', 'image/tiff'];
	const supportedExtensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'];
	const fileName = file.name.toLowerCase();
	const isValidType = supportedTypes.includes(file.type) || 
					   supportedExtensions.some(ext => fileName.endsWith(ext));
	
	if (!isValidType) {
		resultDiv.innerHTML = '<div class="demo-result error">✖ Unsupported file format. Please upload a JPEG, PNG, WebP, BMP, or TIFF image.</div>';
		return;
	}
	
	// Check file size (limit to 5MB for free tier)
	if (file.size > 5 * 1024 * 1024) {
		resultDiv.innerHTML = '<div class="demo-result error">✖ File too large. Please upload an image smaller than 5MB.</div>';
		return;
	}
	
	// Show loading state
	resultDiv.innerHTML = `
		<div class="loading">
			<div class="spinner"></div>
			<p>Processing your image with BackgroundRemover-main...</p>
			<p style="font-size: 0.9em; color: #aaa;">Using advanced AI with alpha matting for better edges</p>
		</div>
	`;
	
	try {
		const formData = new FormData();
		formData.append('file', file);
		formData.append('api_key', apiKey);  // Add API key as form data
		
		// Get form values
		const alphaMatting = document.getElementById('alphaMatting').checked;
		
		formData.append('alpha_matting', alphaMatting);
		
		// Alpha matting parameters (only if enabled)
		if (alphaMatting) {
			formData.append('alpha_matting_foreground_threshold', document.getElementById('foregroundThreshold').value);
			formData.append('alpha_matting_background_threshold', document.getElementById('backgroundThreshold').value);
			formData.append('alpha_matting_erode_structure_size', document.getElementById('erodeSize').value);
			formData.append('alpha_matting_base_size', document.getElementById('baseSize').value);
		}
		
		// Create AbortController for timeout
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes timeout
		
		console.log('Starting background removal request...');
		console.log('API URL:', `${API_BASE_URL}/remove-background`);
		console.log('API Key:', apiKey ? 'Present' : 'Missing');
		
		const response = await fetch(`${API_BASE_URL}/remove-background`, {
			method: 'POST',
			body: formData,
			signal: controller.signal
		});
		
		clearTimeout(timeoutId);
		
		if (!response.ok) {
			const errorData = await response.json();
			throw new Error(errorData.detail || errorData.error || `HTTP error! status: ${response.status}`);
		}
		
		// Handle binary response (PNG image)
		const blob = await response.blob();
		const imageUrl = URL.createObjectURL(blob);
		
		resultDiv.innerHTML = `
			<div class="demo-result success">
				<strong>✓ Background Removed Successfully!</strong><br>
				<strong>Alpha Matting:</strong> ${alphaMatting ? 'Enabled' : 'Disabled'}<br>
				<div style="margin-top: 15px;">
					<strong>Result:</strong><br>
					<img src="${imageUrl}" style="max-width: 100%; border: 1px solid #ddd; border-radius: 5px;" />
				</div>
				<div style="margin-top: 10px;">
					<a href="${imageUrl}" download="processed_image.png" class="button small">Download Image</a>
				</div>
			</div>
		`;
	} catch (error) {
		let errorMessage = error.message;
		
		// Handle specific error types
		if (error.name === 'AbortError') {
			errorMessage = 'Request timed out after 5 minutes. Please try again with a smaller image or check your internet connection.';
		} else if (error.message.includes('Failed to fetch') || error.name === 'TypeError') {
			errorMessage = `Connection Failed: Cannot connect to ${API_BASE_URL}. Make sure the API server is running.`;
		} else if (error.message.includes('NetworkError') || error.message.includes('net::')) {
			errorMessage = 'Network error. Please check your internet connection and try again.';
		}
		
		resultDiv.innerHTML = `<div class="demo-result error">✖ ${errorMessage}</div>`;
	}
}

// Contact Form Functionality
function initializeContactForm() {
	const contactForm = document.getElementById('contactForm');
	if (contactForm) {
		contactForm.addEventListener('submit', handleContactSubmit);
	}
}

async function handleContactSubmit(e) {
	e.preventDefault();
	
	const formData = new FormData(e.target);
	const name = formData.get('name');
	const email = formData.get('email');
	const message = formData.get('message');
	const resultDiv = document.getElementById('contactResult');
	
	// Basic validation
	if (!name.trim() || !email.trim() || !message.trim()) {
		resultDiv.innerHTML = '<div class="demo-result error">Please fill in all fields</div>';
		return;
	}
	
	// Email validation
	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	if (!emailRegex.test(email)) {
		resultDiv.innerHTML = '<div class="demo-result error">Please enter a valid email address</div>';
		return;
	}
	
	// Show loading state
	resultDiv.innerHTML = '<div class="demo-result">📧 Sending message...</div>';
	
	try {
		// Send to backend API
		const response = await fetch(`${API_BASE_URL}/contact`, {
			method: 'POST',
			body: formData
		});
		
		const result = await response.json();
		
		if (result.success) {
			resultDiv.innerHTML = `
				<div class="demo-result success">
					<strong>✓ Message sent successfully!</strong><br>
					We'll get back to you as soon as possible.
				</div>
			`;
			
			// Clear form
			e.target.reset();
		} else {
			throw new Error(result.message || 'Failed to send message');
		}
		
	} catch (error) {
		console.error('Contact form error:', error);
		resultDiv.innerHTML = `
			<div class="demo-result error">
				<strong>✖ Failed to send message</strong><br>
				Please try again or email us directly at:<br>
				<a href="mailto:support@hjbcodeforge.com" style="color: #9bf1ff;">support@hjbcodeforge.com</a>
			</div>
		`;
	}
}

// Event Listeners and Initialization
function initializeDemo() {
	// Check configuration on page load
	checkApiConfiguration();
	
	// Alpha matting controls
	document.getElementById('alphaMatting').addEventListener('change', function() {
		const options = document.getElementById('alphaMattingOptions');
		options.style.display = this.checked ? 'block' : 'none';
	});
	
	// Range input updates
	document.getElementById('foregroundThreshold').addEventListener('input', function() {
		document.getElementById('foregroundValue').textContent = this.value;
	});
	
	document.getElementById('backgroundThreshold').addEventListener('input', function() {
		document.getElementById('backgroundValue').textContent = this.value;
	});
	
	document.getElementById('erodeSize').addEventListener('input', function() {
		document.getElementById('erodeValue').textContent = this.value;
	});
	
	document.getElementById('baseSize').addEventListener('input', function() {
		document.getElementById('baseSizeValue').textContent = this.value;
	});
	
	// Handle drag and drop functionality
	initializeDragAndDrop();
	
	// Initialize contact form
	initializeContactForm();
}

// Drag and Drop Functionality
function initializeDragAndDrop() {
	const imageFile = document.getElementById('imageFile');
	if (imageFile) {
		const dropZone = imageFile.parentElement; // This is now the .file-input-container
		
		['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
			dropZone.addEventListener(eventName, preventDefaults, false);
		});
		
		function preventDefaults(e) {
			e.preventDefault();
			e.stopPropagation();
		}
		
		['dragenter', 'dragover'].forEach(eventName => {
			dropZone.addEventListener(eventName, highlight, false);
		});
		
		['dragleave', 'drop'].forEach(eventName => {
			dropZone.addEventListener(eventName, unhighlight, false);
		});
		
		function highlight(e) {
			dropZone.classList.add('drag-over');
		}
		
		function unhighlight(e) {
			dropZone.classList.remove('drag-over');
		}
		
		dropZone.addEventListener('drop', handleDrop, false);
		
		function handleDrop(e) {
			const dt = e.dataTransfer;
			const files = dt.files;
			
			if (files.length > 0) {
				const file = files[0];
				
				// Validate file type
				const supportedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp', 'image/tiff'];
				const supportedExtensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'];
				const fileName = file.name.toLowerCase();
				const isValidType = supportedTypes.includes(file.type) || 
								   supportedExtensions.some(ext => fileName.endsWith(ext));
				
				if (!isValidType) {
					document.getElementById('imageResult').innerHTML = 
						'<div class="demo-result error">✖ Unsupported file format. Please upload a JPEG, PNG, WebP, BMP, or TIFF image.</div>';
					return;
				}
				
				imageFile.files = files;
				
				// Clear any previous error messages
				const resultDiv = document.getElementById('imageResult');
				if (resultDiv.innerHTML.includes('Unsupported file format')) {
					resultDiv.innerHTML = '';
				}
			}
		}
	}
}

// Reset Alpha Matting Options to Default Values
function resetAlphaMattingOptions() {
	// Define default values
	const defaultValues = {
		foregroundThreshold: 240,
		backgroundThreshold: 10,
		erodeSize: 10,
		baseSize: 1000
	};
	
	// Reset all sliders to default values
	document.getElementById('foregroundThreshold').value = defaultValues.foregroundThreshold;
	document.getElementById('backgroundThreshold').value = defaultValues.backgroundThreshold;
	document.getElementById('erodeSize').value = defaultValues.erodeSize;
	document.getElementById('baseSize').value = defaultValues.baseSize;
	
	// Update the display values
	document.getElementById('foregroundValue').textContent = defaultValues.foregroundThreshold;
	document.getElementById('backgroundValue').textContent = defaultValues.backgroundThreshold;
	document.getElementById('erodeValue').textContent = defaultValues.erodeSize;
	document.getElementById('baseSizeValue').textContent = defaultValues.baseSize;
	
	// Reset the checkbox to checked (default state)
	document.getElementById('alphaMatting').checked = true;
	
	// Show confirmation
	const confirmationDiv = document.createElement('div');
	confirmationDiv.className = 'demo-result success';
	confirmationDiv.style.margin = '10px 0';
	confirmationDiv.innerHTML = '✓ Alpha Matting options reset to default values';
	
	// Insert the confirmation message after the reset button
	const resetButton = document.getElementById('resetButton');
	resetButton.parentNode.insertBefore(confirmationDiv, resetButton.nextSibling);
	
	// Remove the confirmation message after 3 seconds
	setTimeout(() => {
		if (confirmationDiv.parentNode) {
			confirmationDiv.parentNode.removeChild(confirmationDiv);
		}
	}, 3000);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeDemo);
