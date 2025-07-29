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
	const imageFile = document.getElementById('imageFile').files[0];
	const resultDiv = document.getElementById('imageResult');
	const returnJson = document.getElementById('returnJson').checked;
	
	if (!apiKey) {
		showError(resultDiv, 'Please enter your API key');
		return;
	}
	
	if (!imageFile) {
		showError(resultDiv, 'Please select an image');
		return;
	}
	
	// Validate file size
	if (imageFile.size > 5 * 1024 * 1024) {
		showError(resultDiv, 'Image size must be less than 5MB');
		return;
	}
	
	// Show loading state
	showProcessingState(resultDiv, 'Processing image...');
	
	// Get parameters
	const modelHint = document.getElementById('modelHint').value;
	const alphaMatting = document.getElementById('alphaMatting').checked;
	const foregroundThreshold = parseInt(document.getElementById('foregroundThreshold').value);
	const backgroundThreshold = parseInt(document.getElementById('backgroundThreshold').value);
	const erodeSize = parseInt(document.getElementById('erodeSize').value);
	const baseSize = parseInt(document.getElementById('baseSize').value);
	
	// Prepare form data
	const formData = new FormData();
	formData.append('file', imageFile);
	formData.append('api_key', apiKey);
	formData.append('model_hint', modelHint);
	formData.append('alpha_matting', alphaMatting);
	formData.append('alpha_matting_foreground_threshold', foregroundThreshold);
	formData.append('alpha_matting_background_threshold', backgroundThreshold);
	formData.append('alpha_matting_erode_structure_size', erodeSize);
	formData.append('alpha_matting_base_size', baseSize);
	formData.append('return_json', returnJson);
	
	try {
		// Set timeout to 5 minutes for large images
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), 300000);

		showProcessingState(resultDiv, 'Uploading image and processing...');

		let response;
		try {
			response = await fetch('/remove-background', {
				method: 'POST',
				body: formData,
				signal: controller.signal
			});
		} catch (error) {
			if (error.name === 'AbortError') {
				showProcessingState(resultDiv, 'Processing is taking longer than expected...');
				throw new Error('Processing took too long and was cancelled');
			}
			throw error;
		} finally {
			clearTimeout(timeoutId);
		}
		
		if (!response.ok) {
			let errorMessage = 'Failed to remove background';
			try {
				const errorData = await response.json();
				errorMessage = errorData.detail || errorMessage;
			} catch (e) {
				// If parsing JSON fails, use status text
				errorMessage = response.statusText;
			}
			throw new Error(errorMessage);
		}
		
		showProcessingState(resultDiv, 'Processing complete! Loading result...');
		
		if (returnJson) {
			const data = await response.json();
			// Show both the image and processing details
			showResult(resultDiv, data.image, true);
			showProcessingDetails(resultDiv, data.metadata);
		} else {
			const blob = await response.blob();
			if (blob.size === 0) {
				throw new Error('Server returned an empty response');
			}
			showResult(resultDiv, URL.createObjectURL(blob), false);
		}
	} catch (error) {
		let errorMessage = error.message;
		
		// Handle specific error cases
		if (error.name === 'AbortError') {
			errorMessage = 'Processing took too long. Try with a smaller image or disable alpha matting.';
		} else if (error.message.includes('empty response')) {
			errorMessage = 'Processing failed. Try again with alpha matting disabled or use a different image.';
		} else if (!navigator.onLine) {
			errorMessage = 'No internet connection. Please check your connection and try again.';
		} else if (error.message.includes('401')) {
			errorMessage = 'Invalid API key. Please check your API key and try again.';
		} else if (error.message.includes('500')) {
			errorMessage = 'Server error. Please try again with alpha matting disabled or use a different image.';
		}
		
		showError(resultDiv, errorMessage);
		
		// Add retry options
		const retryOptions = document.createElement('div');
		retryOptions.className = 'retry-options';
		
		// If alpha matting was enabled, suggest trying without it
		if (alphaMatting) {
			const retryNoAlphaBtn = document.createElement('button');
			retryNoAlphaBtn.className = 'button primary';
			retryNoAlphaBtn.innerHTML = '<i class="fas fa-redo"></i> Retry without Alpha Matting';
			retryNoAlphaBtn.onclick = () => {
				document.getElementById('alphaMatting').checked = false;
				removeBackground();
			};
			retryOptions.appendChild(retryNoAlphaBtn);
		}
		
		// Add general retry button
		const retryBtn = document.createElement('button');
		retryBtn.className = 'button';
		retryBtn.innerHTML = '<i class="fas fa-redo"></i> Try Again';
		retryBtn.onclick = removeBackground;
		retryOptions.appendChild(retryBtn);
		
		resultDiv.appendChild(retryOptions);
	}
}

function showProcessingState(element, message) {
	element.innerHTML = `
		<div class="processing-state">
			<i class="fas fa-spinner fa-spin" style="font-size:2em;"></i>
			<p>${message}</p>
			<div class="progress-bar-container">
				<div class="progress-bar" id="progressBar"></div>
			</div>
			<p class="processing-note">This may take a while for large images or with alpha matting enabled.<br>If it fails, try disabling alpha matting or using a smaller image.</p>
		</div>
	`;
	// Animate progress bar for user feedback
	const bar = document.getElementById('progressBar');
	if (bar) {
		let width = 0;
		const interval = setInterval(() => {
			width = (width + 1) % 100;
			bar.style.width = width + '%';
		}, 1000);
		// Stop animation when processing is done
		setTimeout(() => clearInterval(interval), 300000);
	}
}

function showError(element, message) {
	element.innerHTML = `
		<div class="error-message">
			<i class="fas fa-exclamation-circle"></i>
			<p>${message}</p>
		</div>
	`;
}

function showResult(element, imageData, isBase64) {
	const img = document.createElement('img');
	img.className = 'result-image';
	img.src = isBase64 ? `data:image/png;base64,${imageData}` : imageData;
	
	const downloadBtn = document.createElement('a');
	downloadBtn.className = 'button primary';
	downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download';
	downloadBtn.href = img.src;
	downloadBtn.download = 'background-removed.png';
	
	element.innerHTML = '';
	element.appendChild(img);
	element.appendChild(downloadBtn);
}

function showProcessingDetails(element, metadata) {
	const details = document.createElement('div');
	details.className = 'processing-details';
	details.innerHTML = `
		<h4>Processing Details:</h4>
		<ul>
			<li>Processing Time: ${metadata.processing_time.toFixed(2)}s</li>
			<li>Model Used: ${metadata.model_used}</li>
			<li>Alpha Matting: ${metadata.alpha_matting_used ? 'Yes' : 'No'}</li>
			${metadata.fallback_used ? '<li><strong>Note:</strong> Used fallback processing method</li>' : ''}
		</ul>
	`;
	element.appendChild(details);
}

// Add CSS for new elements
const style = document.createElement('style');
style.textContent = `
	.processing-state {
		text-align: center;
		padding: 2rem;
	}
	
	.processing-state i {
		font-size: 2rem;
		color: #6cc04a;
		margin-bottom: 1rem;
	}
	
	.processing-note {
		color: #666;
		font-size: 0.9rem;
	}
	
	.error-message {
		background: rgba(255, 0, 0, 0.1);
		border: 1px solid rgba(255, 0, 0, 0.2);
		padding: 1rem;
		border-radius: 0.5rem;
		margin: 1rem 0;
		color: #ff3333;
	}
	
	.error-message i {
		margin-right: 0.5rem;
	}
	
	.result-image {
		max-width: 100%;
		height: auto;
		margin-bottom: 1rem;
		border-radius: 0.5rem;
	}
	
	.processing-details {
		background: rgba(108, 192, 74, 0.1);
		border: 1px solid rgba(108, 192, 74, 0.2);
		padding: 1rem;
		border-radius: 0.5rem;
		margin-top: 1rem;
	}
	
	.processing-details h4 {
		margin: 0 0 0.5rem 0;
		color: #6cc04a;
	}
	
	.processing-details ul {
		margin: 0;
		padding: 0;
		list-style: none;
	}
	
	.processing-details li {
		margin: 0.25rem 0;
	}
`;
document.head.appendChild(style);

// Add CSS for retry options
const styleRetry = document.createElement('style');
styleRetry.textContent = `
	.retry-options {
		margin-top: 1rem;
		display: flex;
		gap: 0.5rem;
		justify-content: center;
	}
	
	.retry-options button {
		min-width: 150px;
	}
	
	.processing-state {
		text-align: center;
		padding: 2rem;
		background: rgba(108, 192, 74, 0.1);
		border: 1px solid rgba(108, 192, 74, 0.2);
		border-radius: 0.5rem;
		margin: 1rem 0;
	}
	
	.processing-state i {
		font-size: 2rem;
		color: #6cc04a;
		margin-bottom: 1rem;
	}
	
	.processing-note {
		color: #666;
		font-size: 0.9rem;
		margin-top: 0.5rem;
	}
	
	.error-message {
		background: rgba(255, 0, 0, 0.1);
		border: 1px solid rgba(255, 0, 0, 0.2);
		padding: 1rem;
		border-radius: 0.5rem;
		margin: 1rem 0;
		color: #ff3333;
		text-align: center;
	}
	
	.error-message i {
		font-size: 1.5rem;
		margin-bottom: 0.5rem;
	}
`;
document.head.appendChild(styleRetry);

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
