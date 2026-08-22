// Background Service Worker - Strict Single Master Mascot Coordinator 🎀

let currentMasterTabId = null;

// Helper to get the truly active tab in the currently focused window
async function getActiveTab() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
    return tab;
  } catch (e) {
    return null;
  }
}

// Switch master active tab
async function setMasterTab(newTabId) {
  if (currentMasterTabId === newTabId && newTabId !== null) return;
  const oldTabId = currentMasterTabId;
  currentMasterTabId = newTabId;

  // Deactivate old tab
  if (oldTabId && oldTabId !== newTabId) {
    chrome.tabs.sendMessage(oldTabId, { action: 'deactivate_pet' }).catch(() => {});
  }

  // Activate new tab
  if (newTabId) {
    chrome.tabs.sendMessage(newTabId, { action: 'activate_pet' }).catch(() => {});
  }
}

// When user clicks / switches tab
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  setMasterTab(activeInfo.tabId);
});

// When browser window focus changes
chrome.windows.onFocusChanged.addListener(async (windowId) => {
  if (windowId === chrome.windows.WINDOW_ID_NONE) {
    // Browser lost focus
    return;
  }
  const tab = await getActiveTab();
  if (tab && tab.id) {
    setMasterTab(tab.id);
  }
});

// When tab is updated/navigated
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.active) {
    setMasterTab(tabId);
  }
});

// When tab is closed
chrome.tabs.onRemoved.addListener((tabId) => {
  if (currentMasterTabId === tabId) {
    currentMasterTabId = null;
    getActiveTab().then(tab => {
      if (tab && tab.id) setMasterTab(tab.id);
    });
  }
});

// Listen for tab registration and claim requests
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'register_tab') {
    const senderTabId = sender.tab ? sender.tab.id : null;
    getActiveTab().then(activeTab => {
      const isCurrent = activeTab && activeTab.id === senderTabId;
      if (isCurrent) {
        currentMasterTabId = senderTabId;
      }
      sendResponse({ isActive: isCurrent });
    });
    return true; // Async response
  }

  if (msg.action === 'claim_master') {
    if (sender.tab && sender.tab.id) {
      setMasterTab(sender.tab.id);
      sendResponse({ status: 'claimed' });
    }
    return true;
  }
});
