const toggle = document.getElementById('toggleDetection');
const status = document.getElementById('status');

// Load saved state
browser.storage.local.get('phishingDetectionEnabled').then(result => {
  toggle.checked = result.phishingDetectionEnabled || false;
  status.textContent = `Status: ${toggle.checked ? "On" : "Off"}`;
});

// Listen for toggle changes
toggle.addEventListener('change', () => {
  const enabled = toggle.checked;
  status.textContent = `Status: ${enabled ? "On" : "Off"}`;
  browser.storage.local.set({ phishingDetectionEnabled: enabled });
  
  browser.tabs.query({ active: true, currentWindow: true }).then(tabs => {
    if (tabs[0].id) {
      browser.tabs.sendMessage(tabs[0].id, { phishingDetectionEnabled: enabled });
    }
  });
});
