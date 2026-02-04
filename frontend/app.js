// API URL - automatically switches between local and production
const API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://url-shortener-production.up.railway.app';  // Update this after Railway deploy

// Store recent URLs in memory
const recentUrls = [];

// DOM Elements
const form = document.getElementById('shorten-form');
const urlInput = document.getElementById('url-input');
const submitBtn = document.getElementById('submit-btn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoading = submitBtn.querySelector('.btn-loading');
const errorMessage = document.getElementById('error-message');
const resultSection = document.getElementById('result');
const shortUrlLink = document.getElementById('short-url');
const originalUrlSpan = document.getElementById('original-url');
const copyBtn = document.getElementById('copy-btn');
const copyMessage = document.getElementById('copy-message');
const recentSection = document.getElementById('recent-section');
const recentList = document.getElementById('recent-list');

// Form submit handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const url = urlInput.value.trim();

    // Basic URL validation
    if (!isValidUrl(url)) {
        showError('Please enter a valid URL (include http:// or https://)');
        return;
    }

    // Show loading state
    setLoading(true);
    hideError();
    hideResult();

    try {
        const response = await fetch(`${API_URL}/api/shorten`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to shorten URL');
        }

        const data = await response.json();

        // Show result
        showResult(data.short_url, data.original_url);

        // Add to recent URLs
        addToRecent(data.short_url, data.original_url);

        // Clear input
        urlInput.value = '';

    } catch (error) {
        showError(error.message || 'Something went wrong. Please try again.');
    } finally {
        setLoading(false);
    }
});

// Copy button handler
copyBtn.addEventListener('click', () => {
    const shortUrl = shortUrlLink.textContent;
    copyToClipboard(shortUrl);
});

// Validate URL format
function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch {
        return false;
    }
}

// Set loading state
function setLoading(loading) {
    submitBtn.disabled = loading;
    btnText.classList.toggle('hidden', loading);
    btnLoading.classList.toggle('hidden', !loading);
}

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

// Hide error message
function hideError() {
    errorMessage.classList.add('hidden');
}

// Show result
function showResult(shortUrl, originalUrl) {
    shortUrlLink.textContent = shortUrl;
    shortUrlLink.href = shortUrl;
    originalUrlSpan.textContent = originalUrl;
    resultSection.classList.remove('hidden');
    copyMessage.classList.add('hidden');
}

// Hide result
function hideResult() {
    resultSection.classList.add('hidden');
}

// Copy to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        copyMessage.classList.remove('hidden');

        // Hide message after 2 seconds
        setTimeout(() => {
            copyMessage.classList.add('hidden');
        }, 2000);
    } catch {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);

        copyMessage.classList.remove('hidden');
        setTimeout(() => {
            copyMessage.classList.add('hidden');
        }, 2000);
    }
}

// Add URL to recent list
function addToRecent(shortUrl, originalUrl) {
    // Add to beginning of array
    recentUrls.unshift({ shortUrl, originalUrl });

    // Keep only last 5
    if (recentUrls.length > 5) {
        recentUrls.pop();
    }

    // Update display
    displayRecentUrls();
}

// Display recent URLs
function displayRecentUrls() {
    if (recentUrls.length === 0) {
        recentSection.classList.add('hidden');
        return;
    }

    recentSection.classList.remove('hidden');
    recentList.innerHTML = '';

    recentUrls.forEach(({ shortUrl, originalUrl }) => {
        const li = document.createElement('li');
        li.className = 'recent-item';
        li.innerHTML = `
            <a href="${shortUrl}" target="_blank" class="recent-short">${shortUrl}</a>
            <span class="recent-original">${originalUrl}</span>
        `;
        recentList.appendChild(li);
    });
}
