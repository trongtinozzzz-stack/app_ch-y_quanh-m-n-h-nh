// Chrome Extension Content Script - Strict Single Master Anya Instance 🎀
(function () {
  if (window.__ANYA_DESKTOP_PET_INJECTED__) return;
  window.__ANYA_DESKTOP_PET_INJECTED__ = true;

  let config = {
    enabled: true,
    sound_enabled: true,
    scale: 1.0,
    speed: 3,
    gemini_api_key: ""
  };

  const State = {
    IDLE: 'idle',
    WALK_LEFT: 'walk_left',
    WALK_RIGHT: 'walk_right',
    CLICKED: 'clicked',
    DRAGGED: 'dragged',
    FALLING: 'falling'
  };

  // Strict Master Tab State (Hidden by default until authorized)
  let isMasterActive = false;
  let currentState = State.IDLE;
  let posX = Math.max(20, (window.innerWidth || 1024) - 220);
  let posY = Math.max(20, (window.innerHeight || 768) - 230);
  let isDragging = false;
  let isFalling = false;
  let dragStartX = 0;
  let dragStartY = 0;
  let hasDraggedFar = false;
  let bubbleTimeout = null;
  let stateTimer = null;
  let frameIndex = 0;
  let lastFrameTime = performance.now();

  // Sprites URLs & Preload
  const spriteUrls = {
    [State.IDLE]: [
      chrome.runtime.getURL('assets/sprites/idle_1.png'),
      chrome.runtime.getURL('assets/sprites/idle_2.png')
    ],
    [State.WALK_LEFT]: [
      chrome.runtime.getURL('assets/sprites/walk_l1.png'),
      chrome.runtime.getURL('assets/sprites/walk_l2.png')
    ],
    [State.WALK_RIGHT]: [
      chrome.runtime.getURL('assets/sprites/walk_r1.png'),
      chrome.runtime.getURL('assets/sprites/walk_r2.png')
    ],
    [State.CLICKED]: [chrome.runtime.getURL('assets/sprites/clicked.png')],
    [State.DRAGGED]: [chrome.runtime.getURL('assets/sprites/dragged.png')],
    [State.FALLING]: [chrome.runtime.getURL('assets/sprites/dragged.png')]
  };

  for (let key in spriteUrls) {
    spriteUrls[key].forEach(url => {
      const img = new Image();
      img.src = url;
    });
  }

  const soundNames = [
    'waku_waku.wav',
    'happy_jingle.wav',
    'drop_bell.wav',
    'boing_jump.wav',
    'cute_chirp.wav',
    'cute_poyo.wav',
    'magic_sparkle.wav',
    'pop_bubble.wav'
  ];

  const soundCache = {};
  soundNames.forEach(name => {
    try {
      const audio = new Audio(chrome.runtime.getURL(`assets/sounds/${name}`));
      audio.preload = 'auto';
      audio.volume = 0.6;
      soundCache[name] = audio;
    } catch (e) {}
  });

  function playSound(name) {
    if (!config.sound_enabled || !isMasterActive) return;
    try {
      const audio = soundCache[name] || new Audio(chrome.runtime.getURL(`assets/sounds/${name}`));
      audio.currentTime = 0;
      audio.volume = 0.6;
      audio.play().catch(() => {});
    } catch (e) {}
  }

  function playRandomSound() {
    if (!config.sound_enabled || !isMasterActive) return;
    const r = Math.floor(Math.random() * soundNames.length);
    playSound(soundNames[r]);
  }

  // Create UI Root (Starts Hidden)
  const root = document.createElement('div');
  root.id = 'anya-pet-root';
  root.style.display = 'none';

  const container = document.createElement('div');
  container.className = 'anya-pet-container';

  const bubble = document.createElement('div');
  bubble.className = 'anya-bubble anya-hidden';
  bubble.innerHTML = `
    <div class="anya-bubble-text">Waku Waku! ✨</div>
    <div class="anya-bubble-arrow"></div>
  `;

  const chatBox = document.createElement('div');
  chatBox.className = 'anya-chat-box anya-hidden';
  chatBox.innerHTML = `
    <input type="text" placeholder="Hỏi Anya điều gì đó..." autocomplete="off" />
    <button title="Gửi">🌸</button>
  `;

  const spriteWrapper = document.createElement('div');
  spriteWrapper.className = 'anya-sprite-wrapper';

  const img = document.createElement('img');
  img.src = spriteUrls[State.IDLE][0];
  img.alt = 'Anya Mascot';

  const shadow = document.createElement('div');
  shadow.className = 'anya-shadow';

  spriteWrapper.appendChild(img);
  spriteWrapper.appendChild(shadow);

  container.appendChild(bubble);
  container.appendChild(chatBox);
  container.appendChild(spriteWrapper);
  root.appendChild(container);

  function mountToDOM() {
    const parent = document.body || document.documentElement;
    if (parent && !document.getElementById('anya-pet-root')) {
      parent.appendChild(root);
      updatePosition();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountToDOM);
  } else {
    mountToDOM();
  }

  const bubbleText = bubble.querySelector('.anya-bubble-text');
  const chatInput = chatBox.querySelector('input');
  const chatSendBtn = chatBox.querySelector('button');

  function saveGlobalPosition() {
    if (chrome.storage && chrome.storage.local) {
      chrome.storage.local.set({
        sync_posX: Math.round(posX),
        sync_posY: Math.round(posY)
      });
    }
  }

  function updatePosition() {
    container.style.transform = `translate3d(${Math.round(posX)}px, ${Math.round(posY)}px, 0)`;
  }

  function applyMasterVisibility() {
    if (isMasterActive && config.enabled) {
      root.style.display = 'block';
      spriteWrapper.style.transform = `scale(${config.scale || 1.0})`;
    } else {
      root.style.display = 'none';
      if (bubbleTimeout) clearTimeout(bubbleTimeout);
    }
  }

  function activatePet() {
    isMasterActive = true;
    if (chrome.storage && chrome.storage.local) {
      chrome.storage.local.get(['sync_posX', 'sync_posY'], (items) => {
        if (items && items.sync_posX !== undefined) {
          posX = Math.max(10, Math.min((window.innerWidth || 1024) - 200, items.sync_posX));
          posY = Math.max(10, Math.min((window.innerHeight || 768) - 220, items.sync_posY));
          updatePosition();
        }
      });
    }
    applyMasterVisibility();
  }

  function deactivatePet() {
    isMasterActive = false;
    applyMasterVisibility();
  }

  // Register tab on load
  chrome.runtime.sendMessage({ action: 'register_tab' }, (response) => {
    if (response && response.isActive) {
      activatePet();
    } else {
      deactivatePet();
    }
  });

  // Claim master tab on window focus or user click
  window.addEventListener('focus', () => {
    chrome.runtime.sendMessage({ action: 'claim_master' });
  });

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      chrome.runtime.sendMessage({ action: 'claim_master' });
    } else {
      deactivatePet();
    }
  });

  const quotes = [
    "Waku Waku! ✨",
    "Anya đang ngắm bạn lướt web nè! 🎀",
    "Thích ăn đậu phộng nhất trần đời! 🥜",
    "Hehehe, Anya đọc được suy nghĩ đó! 🌸",
    "Lướt web nhớ uống nước nha sen ơi! 💧",
    "Bé ngoan ở đây bảo vệ sen nè! 🚀",
    "Anya thích khám phá thế giới! 💖"
  ];

  function showBubble(text, duration = 3000) {
    if (!isMasterActive) return;
    if (bubbleTimeout) clearTimeout(bubbleTimeout);
    bubbleText.textContent = text;
    bubble.classList.remove('anya-hidden');
    bubble.classList.add('visible');

    bubbleTimeout = setTimeout(() => {
      bubble.classList.remove('visible');
      bubble.classList.add('anya-hidden');
    }, duration);
  }

  function spawnParticles(count = 5) {
    if (!isMasterActive) return;
    const icons = ['✨', '💖', '⭐', '🌸', '🥜', '🎀'];
    const parent = document.body || document.documentElement;
    for (let i = 0; i < count; i++) {
      const p = document.createElement('div');
      p.className = 'anya-particle';
      p.textContent = icons[Math.floor(Math.random() * icons.length)];
      p.style.left = `${posX + 70 + (Math.random() * 40 - 20)}px`;
      p.style.top = `${posY + 70 + (Math.random() * 40 - 20)}px`;
      parent.appendChild(p);

      setTimeout(() => {
        if (p.parentNode) p.parentNode.removeChild(p);
      }, 800);
    }
  }

  function updateSprite() {
    const list = spriteUrls[currentState] || spriteUrls[State.IDLE];
    frameIndex = (frameIndex + 1) % list.length;
    img.src = list[frameIndex];
  }

  function setState(newState, duration = null) {
    if (currentState === newState && !duration) return;
    currentState = newState;
    frameIndex = 0;
    updateSprite();

    if (stateTimer) clearTimeout(stateTimer);
    if (duration) {
      stateTimer = setTimeout(() => {
        chooseNextAIAction();
      }, duration);
    }
  }

  function chooseNextAIAction() {
    if (isDragging || isFalling || !chatBox.classList.contains('anya-hidden')) return;

    const r = Math.random();
    if (r < 0.45) {
      setState(State.WALK_LEFT, 2500 + Math.random() * 3000);
    } else if (r < 0.9) {
      setState(State.WALK_RIGHT, 2500 + Math.random() * 3000);
    } else {
      setState(State.IDLE, 3000 + Math.random() * 4000);
      if (Math.random() < 0.35 && isMasterActive) {
        showBubble(quotes[Math.floor(Math.random() * quotes.length)], 3000);
      }
    }
  }

  // Animation Loop
  let lastTime = performance.now();
  let syncPosTimer = 0;
  function loop(now) {
    const dt = Math.min((now - lastTime) / 1000, 0.05);
    lastTime = now;

    if (isMasterActive && config.enabled) {
      if (now - lastFrameTime > 200) {
        lastFrameTime = now;
        updateSprite();
      }

      if (!isDragging && !isFalling) {
        const speed = (config.speed || 3) * 30 * dt;

        if (currentState === State.WALK_LEFT) {
          posX -= speed;
          if (posX <= 10) {
            posX = 10;
            setState(State.WALK_RIGHT, 3000 + Math.random() * 2000);
          }
          updatePosition();
        } else if (currentState === State.WALK_RIGHT) {
          posX += speed;
          const maxW = (window.innerWidth || 1024) - 200;
          if (posX >= maxW) {
            posX = maxW;
            setState(State.WALK_LEFT, 3000 + Math.random() * 2000);
          }
          updatePosition();
        }

        syncPosTimer += dt;
        if (syncPosTimer > 1.0) {
          syncPosTimer = 0;
          saveGlobalPosition();
        }
      }
    }

    requestAnimationFrame(loop);
  }

  // Smooth Gravity Fall
  let velocityY = 0;
  const gravity = 2200;

  function startFall() {
    isFalling = true;
    velocityY = 0;
    setState(State.FALLING);

    let lastFall = performance.now();
    function step(t) {
      if (!isFalling || isDragging) return;
      const dt = Math.min((t - lastFall) / 1000, 0.05);
      lastFall = t;

      velocityY += gravity * dt;
      posY += velocityY * dt;

      const floorY = (window.innerHeight || 768) - 220;
      if (posY >= floorY) {
        posY = floorY;
        isFalling = false;
        updatePosition();
        saveGlobalPosition();
        playSound('drop_bell.wav');
        spawnParticles(6);
        setState(State.CLICKED, 800);
        return;
      }

      updatePosition();
      requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  // Drag & Drop
  container.addEventListener('mousedown', (e) => {
    if (e.button !== 0) return;
    chrome.runtime.sendMessage({ action: 'claim_master' });
    isDragging = true;
    hasDraggedFar = false;
    dragStartX = e.clientX - posX;
    dragStartY = e.clientY - posY;
    container.classList.add('grabbing');
    setState(State.DRAGGED);
  });

  window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const newX = e.clientX - dragStartX;
    const newY = e.clientY - dragStartY;

    if (Math.abs(newX - posX) > 3 || Math.abs(newY - posY) > 3) {
      hasDraggedFar = true;
    }

    posX = Math.max(0, Math.min((window.innerWidth || 1024) - 180, newX));
    posY = Math.max(0, Math.min((window.innerHeight || 768) - 180, newY));
    updatePosition();
  });

  window.addEventListener('mouseup', () => {
    if (!isDragging) return;
    isDragging = false;
    container.classList.remove('grabbing');

    if (hasDraggedFar) {
      startFall();
    } else {
      handlePetClick();
    }
    saveGlobalPosition();
  });

  function handlePetClick() {
    playRandomSound();
    spawnParticles(8);
    setState(State.CLICKED, 1200);
    showBubble(quotes[Math.floor(Math.random() * quotes.length)], 2500);
  }

  container.addEventListener('dblclick', () => {
    openChatBox();
  });

  container.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    openChatBox();
  });

  function openChatBox() {
    chatBox.classList.remove('anya-hidden');
    chatInput.focus();
    showBubble("Anya đang nghe nè, bạn muốn hỏi gì? ✨", 3000);
  }

  async function handleSendChat() {
    const text = chatInput.value.trim();
    if (!text) return;

    chatBox.classList.add('anya-hidden');
    showBubble("Anya đang suy nghĩ... 🤔💭", 10000);
    setState(State.CLICKED);

    const apiKey = config.gemini_api_key;
    if (!apiKey) {
      showBubble("Bạn chưa nhập Gemini API Key trong menu cài đặt tiện ích kìa! 🌸", 4000);
      return;
    }

    try {
      const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;
      const systemInstruction = "Bạn là bé Anya Forger dễ thương trong Spy x Family. Bạn là desktop pet đang chạy trên trình duyệt web. Hãy trả lời ngắn gọn (1-2 câu), vui tươi bằng tiếng Việt, thỉnh thoảng dùng 'Waku waku!'";

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ role: "user", parts: [{ text: `${systemInstruction}\n\nNgười dùng hỏi: "${text}"` }] }]
        })
      });

      const data = await res.json();
      if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
        showBubble(data.candidates[0].content.parts[0].text.trim(), 6000);
        playSound('cute_chirp.wav');
        spawnParticles(6);
      } else {
        showBubble("Anya chưa hiểu lắm, bạn hỏi lại nha!", 3000);
      }
    } catch (err) {
      showBubble("Opps! Có trục trặc mạng rùi nha!", 3000);
    } finally {
      setTimeout(chooseNextAIAction, 3500);
    }
  }

  chatSendBtn.addEventListener('click', handleSendChat);
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleSendChat();
    if (e.key === 'Escape') chatBox.classList.add('anya-hidden');
  });

  window.addEventListener('resize', () => {
    posX = Math.min(posX, Math.max(10, (window.innerWidth || 1024) - 200));
    posY = Math.min(posY, Math.max(10, (window.innerHeight || 768) - 220));
    updatePosition();
  });

  // Listen for messages from background & popup
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.action === 'activate_pet') {
      activatePet();
      sendResponse({ status: 'activated' });
    } else if (msg.action === 'deactivate_pet') {
      deactivatePet();
      sendResponse({ status: 'deactivated' });
    } else if (msg.action === 'summon') {
      config.enabled = true;
      activatePet();
      posX = Math.round(window.innerWidth / 2 - 100);
      posY = Math.round(window.innerHeight - 230);
      updatePosition();
      saveGlobalPosition();
      playSound('waku_waku.wav');
      spawnParticles(10);
      setState(State.CLICKED, 1500);
      showBubble("Tadaaa! Bé Anya đã tới rồi nè! 🎀", 3500);
      sendResponse({ success: true });
    } else if (msg.action === 'dance') {
      playSound('happy_jingle.wav');
      spawnParticles(8);
      setState(State.CLICKED, 2000);
      showBubble("Waku Waku nhảy múa vui quá! 💃✨", 3000);
      sendResponse({ success: true });
    } else if (msg.action === 'say_hi') {
      handlePetClick();
      sendResponse({ success: true });
    }
  });

  if (chrome.storage && chrome.storage.local) {
    chrome.storage.local.get(['enabled', 'sound_enabled', 'scale', 'speed', 'gemini_api_key', 'sync_posX', 'sync_posY'], (res) => {
      if (res) {
        config = { ...config, ...res };
        if (res.sync_posX !== undefined) posX = res.sync_posX;
        if (res.sync_posY !== undefined) posY = res.sync_posY;
      }
      applyMasterVisibility();
      updatePosition();
    });

    chrome.storage.onChanged.addListener((changes, area) => {
      if (area === 'local') {
        for (let key in changes) {
          config[key] = changes[key].newValue;
        }
        applyMasterVisibility();
      }
    });
  }

  // Init
  posY = Math.max(20, (window.innerHeight || 768) - 230);
  posX = Math.max(20, (window.innerWidth || 1024) - 220);
  updatePosition();
  requestAnimationFrame(loop);
  chooseNextAIAction();
})();
