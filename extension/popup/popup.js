document.addEventListener('DOMContentLoaded', () => {
  const toggleEnabled = document.getElementById('toggle-enabled');
  const toggleSound = document.getElementById('toggle-sound');
  const sliderScale = document.getElementById('slider-scale');
  const scaleVal = document.getElementById('scale-val');
  const sliderSpeed = document.getElementById('slider-speed');
  const speedVal = document.getElementById('speed-val');
  const apiKeyInput = document.getElementById('api-key');
  const saveBtn = document.getElementById('save-btn');
  const statusMsg = document.getElementById('status-msg');
  const btnSummon = document.getElementById('btn-summon');
  const btnPlayground = document.getElementById('btn-playground');
  const btnOpenGoogle = document.getElementById('btn-open-google');

  // Load saved settings
  chrome.storage.local.get(
    {
      enabled: true,
      sound_enabled: true,
      scale: 1.0,
      speed: 3,
      gemini_api_key: ''
    },
    (items) => {
      toggleEnabled.checked = items.enabled;
      toggleSound.checked = items.sound_enabled;

      const scalePct = Math.round(items.scale * 100);
      sliderScale.value = scalePct;
      scaleVal.textContent = `${scalePct}%`;

      sliderSpeed.value = items.speed;
      speedVal.textContent = `${items.speed}`;

      apiKeyInput.value = items.gemini_api_key || '';
    }
  );

  sliderScale.addEventListener('input', () => {
    scaleVal.textContent = `${sliderScale.value}%`;
  });

  sliderSpeed.addEventListener('input', () => {
    speedVal.textContent = `${sliderSpeed.value}`;
  });

  // Save Settings
  function saveCurrentSettings(callback) {
    const newSettings = {
      enabled: toggleEnabled.checked,
      sound_enabled: toggleSound.checked,
      scale: parseInt(sliderScale.value, 10) / 100,
      speed: parseInt(sliderSpeed.value, 10),
      gemini_api_key: apiKeyInput.value.trim()
    };

    chrome.storage.local.set(newSettings, () => {
      if (callback) callback();
    });
  }

  saveBtn.addEventListener('click', () => {
    saveCurrentSettings(() => {
      statusMsg.textContent = '✨ Đã lưu cài đặt thành công!';
      setTimeout(() => {
        statusMsg.textContent = '';
      }, 2000);
    });
  });

  // Open Playground
  btnPlayground.addEventListener('click', () => {
    chrome.tabs.create({ url: chrome.runtime.getURL('playground.html') });
  });

  // Open Google.com
  btnOpenGoogle.addEventListener('click', () => {
    chrome.tabs.create({ url: 'https://www.google.com' });
  });

  // Summon Anya to active tab
  btnSummon.addEventListener('click', async () => {
    toggleEnabled.checked = true;
    saveCurrentSettings();

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab && tab.id) {
        chrome.tabs.sendMessage(tab.id, { action: 'summon' }, (response) => {
          if (chrome.runtime.lastError) {
            statusMsg.textContent = '⚠️ Hãy bấm "Sân chơi Anya" hoặc mở Google.com!';
          } else {
            statusMsg.textContent = '🎀 Anya đã xuất hiện trên trang!';
          }
          setTimeout(() => { statusMsg.textContent = ''; }, 3000);
        });
      }
    } catch (e) {
      statusMsg.textContent = '⚠️ Hãy mở 1 trang web thực tế!';
    }
  });
});
