const data = JSON.parse(localStorage.getItem('flashCardUser'));


// Send the data to the background script
chrome.runtime.sendMessage({ type: 'FROM_CONTENT_SCRIPT', payload: 1 });