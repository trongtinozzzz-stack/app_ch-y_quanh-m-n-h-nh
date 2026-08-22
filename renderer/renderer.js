// Desktop Pet Mascot - Ultra-Smooth Renderer Engine
(async function () {
  // DOM Elements
  const petContainer = document.getElementById('pet-container');
  const petImage = document.getElementById('pet-image');
  const petSpriteWrapper = document.getElementById('pet-sprite-wrapper');
  const speechBubble = document.getElementById('speech-bubble');
  const bubbleText = document.getElementById('bubble-text');
  const chatBox = document.getElementById('chat-box');
  const chatInput = document.getElementById('chat-input');
  const chatSendBtn = document.getElementById('chat-send-btn');
  const particlesContainer = document.getElementById('particles-container');

  const contextMenu = document.getElementById('context-menu');
  const menuChat = document.getElementById('menu-chat');
  const menuCustomAvatar = document.getElementById('menu-custom-avatar');
  const menuRestoreAnya = document.getElementById('menu-restore-anya');
  const menuToggleSound = document.getElementById('menu-toggle-sound');
  const soundIcon = document.getElementById('sound-icon');
  const soundText = document.getElementById('sound-text');
  const menuSettings = document.getElementById('menu-settings');
  const menuQuit = document.getElementById('menu-quit');

  const settingsModal = document.getElementById('settings-modal');
  const closeSettingsBtn = document.getElementById('close-settings-btn');
  const saveSettingsBtn = document.getElementById('save-settings-btn');
  const scaleSlider = document.getElementById('scale-slider');
  const scaleValue = document.getElementById('scale-value');
  const speedSlider = document.getElementById('speed-slider');
  const speedValue = document.getElementById('speed-value');
  const apiKeyInput = document.getElementById('api-key-input');

  // App State
  const State = {
    IDLE: 'idle',
    WALK_LEFT: 'walk_left',
    WALK_RIGHT: 'walk_right',
    CLICKED: 'clicked',
    DRAGGED: 'dragged',
    FALLING: 'falling'
  };

  let currentState = State.IDLE;
  let customAvatarUrl = null;
  let isDragging = false;
  let isFalling = false;
  let dragStartX = 0;
  let dragStartY = 0;
  let hasDraggedFar = false;

  let bubbleTimeout = null;
  let stateTimer = null;
  let frameIndex = 0;
  let lastFrameTime = performance.now();

  // Local Window Coordinates & Screen Cache (eliminates IPC lag)
  let winX = 1000;
  let winY = 800;
  let winWidth = 200;
  let winHeight = 220;
  let screenBounds = { x: 0, y: 0, width: 1920, height: 1080 };

  // Config defaults
  let config = {
    gemini_api_key: "",
    sound_enabled: true,
    scale: 1.0,
    speed: 3
  };

  // Pre-decode and preload Sprites for 0ms lag
  const spritePaths = {
    [State.IDLE]: ['../assets/sprites/idle_1.png', '../assets/sprites/idle_2.png'],
    [State.WALK_LEFT]: ['../assets/sprites/walk_l1.png', '../assets/sprites/walk_l2.png'],
    [State.WALK_RIGHT]: ['../assets/sprites/walk_r1.png', '../assets/sprites/walk_r2.png'],
    [State.CLICKED]: ['../assets/sprites/clicked.png'],
    [State.DRAGGED]: ['../assets/sprites/dragged.png'],
    [State.FALLING]: ['../assets/sprites/dragged.png']
  };

  const imageCache = {};
  for (let key in spritePaths) {
    imageCache[key] = spritePaths[key].map(src => {
      const img = new Image();
      img.src = src;
      return img;
    });
  }

  // Preload Audio
  const soundFiles = [
    'waku_waku.wav',
    'happy_jingle.wav',
    'drop_bell.wav',
    'boing_jump.wav',
    'cute_chirp.wav',
    'cute_poyo.wav',
    'cute_squeak.wav',
    'magic_sparkle.wav',
    'meow.wav',
    'pop1.wav',
    'pop2.wav',
    'pop_bubble.wav',
    'soft_meow.wav'
  ];

  const audioCache = {};
  soundFiles.forEach(file => {
    const audio = new Audio(`../assets/sounds/${file}`);
    audio.preload = 'auto';
    audioCache[file] = audio;
  });

  function playSound(name) {
    if (!config.sound_enabled) return;
    const audio = audioCache[name];
    if (audio) {
      try {
        audio.currentTime = 0;
        audio.play().catch(() => {});
      } catch (e) {}
    }
  }

  function playRandomSound() {
    if (!config.sound_enabled) return;
    const randomIndex = Math.floor(Math.random() * soundFiles.length);
    playSound(soundFiles[randomIndex]);
  }

  // Init Config & Coordinates
  async function initEngine() {
    try {
      const loaded = await window.electronAPI.getConfig();
      if (loaded) config = { ...config, ...loaded };

      const bounds = await window.electronAPI.getScreenBounds();
      if (bounds) screenBounds = bounds;

      const pos = await window.electronAPI.getWindowPosition();
      if (pos) {
        winX = pos.x;
        winY = pos.y;
        winWidth = pos.width || 200;
        winHeight = pos.height || 220;
      }
    } catch (e) {}

    if (window.electronAPI.onScreenChanged) {
      window.electronAPI.onScreenChanged((newBounds) => {
        screenBounds = newBounds;
      });
    }

    applyConfigUI();
  }

  function applyConfigUI() {
    soundIcon.textContent = config.sound_enabled ? '🔊' : '🔇';
    soundText.textContent = `Âm thanh: ${config.sound_enabled ? 'Bật' : 'Tắt'}`;

    const scalePercent = Math.round((config.scale || 1.0) * 100);
    scaleSlider.value = scalePercent;
    scaleValue.textContent = `${scalePercent}%`;
    petSpriteWrapper.style.transform = `scale(${config.scale || 1.0})`;

    speedSlider.value = config.speed || 3;
    speedValue.textContent = `${config.speed || 3}`;

    apiKeyInput.value = config.gemini_api_key || '';
  }

  const defaultQuotes = [
    "Waku Waku! ✨",
    "Anya thích ăn đậu phộng nhất! 🥜",
    "Hehe, hôm nay sen thế nào? 🌸",
    "Anya đọc được suy nghĩ đó nha! 🕵️‍♀️",
    "Bé ngoan chờ bạn làm việc nè! 🎀",
    "Waku waku wakuuu! 🚀",
    "Nhớ uống nước nhé sen ơi! 💧",
    "Tập trung làm việc kiếm tiền mua đậu phộng nào! 💖"
  ];

  function showBubble(text, duration = 3500) {
    if (bubbleTimeout) clearTimeout(bubbleTimeout);
    bubbleText.textContent = text;
    speechBubble.classList.remove('hidden');
    speechBubble.classList.add('visible');

    bubbleTimeout = setTimeout(() => {
      speechBubble.classList.remove('visible');
    }, duration);
  }

  const particleIcons = ['✨', '💖', '⭐', '🌸', '🎵', '🥜', '🎀'];
  function spawnParticles(count = 5) {
    for (let i = 0; i < count; i++) {
      const p = document.createElement('div');
      p.className = 'particle';
      p.textContent = particleIcons[Math.floor(Math.random() * particleIcons.length)];
      p.style.left = `${30 + Math.random() * 40}%`;
      p.style.bottom = `${30 + Math.random() * 30}%`;
      particlesContainer.appendChild(p);

      setTimeout(() => {
        if (p.parentNode) p.parentNode.removeChild(p);
      }, 800);
    }
  }

  // Smooth Sprite Animation Frame
  function updateSpriteFrame() {
    if (customAvatarUrl) {
      petImage.src = customAvatarUrl;
      return;
    }

    const frameList = spritePaths[currentState] || spritePaths[State.IDLE];
    if (!frameList || frameList.length === 0) return;

    frameIndex = (frameIndex + 1) % frameList.length;
    petImage.src = frameList[frameIndex];
  }

  function setState(newState, duration = null) {
    if (currentState === newState && !duration) return;
    currentState = newState;
    frameIndex = 0;
    updateSpriteFrame();

    if (stateTimer) clearTimeout(stateTimer);

    if (duration) {
      stateTimer = setTimeout(() => {
        chooseNextAIAction();
      }, duration);
    }
  }

  function chooseNextAIAction() {
    if (isDragging || isFalling || !chatBox.classList.contains('hidden')) {
      return;
    }

    const rand = Math.random();
    if (rand < 0.45) {
      setState(State.WALK_LEFT, 2500 + Math.random() * 3500);
    } else if (rand < 0.9) {
      setState(State.WALK_RIGHT, 2500 + Math.random() * 3500);
    } else {
      setState(State.IDLE, 3000 + Math.random() * 5000);
      if (Math.random() < 0.4) {
        const quote = defaultQuotes[Math.floor(Math.random() * defaultQuotes.length)];
        showBubble(quote, 3000);
      }
    }
  }

  // Ultra-Smooth 60-144 FPS Movement Loop with fast IPC
  let lastLoopTime = performance.now();
  function movementLoop(currentTime) {
    const dt = Math.min((currentTime - lastLoopTime) / 1000, 0.05);
    lastLoopTime = currentTime;

    // Sprite frame timer (200ms per frame)
    if (currentTime - lastFrameTime > 200) {
      lastFrameTime = currentTime;
      updateSpriteFrame();
    }

    if (!isDragging && !isFalling) {
      const speed = (config.speed || 3) * 30 * dt;

      if (currentState === State.WALK_LEFT) {
        winX -= speed;
        if (winX <= screenBounds.x + 5) {
          winX = screenBounds.x + 5;
          setState(State.WALK_RIGHT, 3000 + Math.random() * 3000);
        }
        if (window.electronAPI.setPosFast) {
          window.electronAPI.setPosFast(winX, winY);
        }
      } else if (currentState === State.WALK_RIGHT) {
        winX += speed;
        const maxRight = screenBounds.x + screenBounds.width - winWidth - 5;
        if (winX >= maxRight) {
          winX = maxRight;
          setState(State.WALK_LEFT, 3000 + Math.random() * 3000);
        }
        if (window.electronAPI.setPosFast) {
          window.electronAPI.setPosFast(winX, winY);
        }
      }
    }

    requestAnimationFrame(movementLoop);
  }

  // Smooth Gravity Fall
  let fallVelocityY = 0;
  const gravity = 2200;

  function startGravityFall() {
    isFalling = true;
    fallVelocityY = 0;
    petContainer.classList.add('falling');
    setState(State.FALLING);

    let lastFallTime = performance.now();

    function fallStep(time) {
      if (!isFalling || isDragging) return;

      const dt = Math.min((time - lastFallTime) / 1000, 0.05);
      lastFallTime = time;

      fallVelocityY += gravity * dt;
      winY += fallVelocityY * dt;

      const targetFloorY = screenBounds.y + screenBounds.height - winHeight;

      if (winY >= targetFloorY) {
        winY = targetFloorY;
        if (window.electronAPI.setPosFast) {
          window.electronAPI.setPosFast(winX, winY);
        }
        isFalling = false;
        petContainer.classList.remove('falling');
        playSound('drop_bell.wav');
        spawnParticles(6);
        setState(State.CLICKED, 800);
        return;
      } else {
        if (window.electronAPI.setPosFast) {
          window.electronAPI.setPosFast(winX, winY);
        }
        requestAnimationFrame(fallStep);
      }
    }

    requestAnimationFrame(fallStep);
  }

  // Mouse Interactions
  petContainer.addEventListener('mousedown', (e) => {
    if (e.button !== 0) return;
    hideContextMenu();

    isDragging = true;
    hasDraggedFar = false;
    dragStartX = e.screenX;
    dragStartY = e.screenY;
    petContainer.classList.add('grabbing');
    setState(State.DRAGGED);
  });

  window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;

    const dx = e.screenX - dragStartX;
    const dy = e.screenY - dragStartY;

    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
      hasDraggedFar = true;
    }

    winX += dx;
    winY += dy;
    dragStartX = e.screenX;
    dragStartY = e.screenY;

    if (window.electronAPI.setPosFast) {
      window.electronAPI.setPosFast(winX, winY);
    }
  });

  window.addEventListener('mouseup', () => {
    if (!isDragging) return;
    isDragging = false;
    petContainer.classList.remove('grabbing');

    if (hasDraggedFar) {
      startGravityFall();
    } else {
      handlePetClick();
    }
  });

  function handlePetClick() {
    playRandomSound();
    spawnParticles(8);
    setState(State.CLICKED, 1200);

    const clickQuotes = [
      "Waku Waku! ✨",
      "Hehehe! 🌸",
      "Đậu phộng! Đậu phộng! 🥜",
      "Anya thích được cưng nựng! 🎀",
      "Bùm chíu! 💥",
      "Kyaaa dễ thương quá! 💖"
    ];
    const q = clickQuotes[Math.floor(Math.random() * clickQuotes.length)];
    showBubble(q, 2000);
  }

  // Context Menu
  window.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    showContextMenu(e.clientX, e.clientY);
  });

  function showContextMenu(x, y) {
    contextMenu.style.left = `${Math.min(x, 10)}px`;
    contextMenu.style.top = `${Math.max(10, Math.min(y, 40))}px`;
    contextMenu.classList.remove('hidden');
  }

  function hideContextMenu() {
    contextMenu.classList.add('hidden');
  }

  window.addEventListener('click', (e) => {
    if (!contextMenu.contains(e.target)) {
      hideContextMenu();
    }
  });

  menuChat.addEventListener('click', () => {
    hideContextMenu();
    openChatBox();
  });

  menuCustomAvatar.addEventListener('click', async () => {
    hideContextMenu();
    try {
      const res = await window.electronAPI.openImageDialog();
      if (res && res.dataUrl) {
        customAvatarUrl = res.dataUrl;
        updateSpriteFrame();
        showBubble("Avatar mới xinh xắn quá! ✨", 3000);
        playSound('magic_sparkle.wav');
        spawnParticles(10);
      }
    } catch (e) {}
  });

  menuRestoreAnya.addEventListener('click', () => {
    hideContextMenu();
    customAvatarUrl = null;
    updateSpriteFrame();
    showBubble("Đã khôi phục bé Anya gốc rùi nè! 🎀", 3000);
    playSound('happy_jingle.wav');
    spawnParticles(8);
  });

  menuToggleSound.addEventListener('click', async () => {
    config.sound_enabled = !config.sound_enabled;
    await window.electronAPI.saveConfig({ sound_enabled: config.sound_enabled });
    applyConfigUI();
    showBubble(config.sound_enabled ? "Đã bật âm thanh! 🔊" : "Đã tắt âm thanh! 🔇", 2000);
    hideContextMenu();
  });

  menuSettings.addEventListener('click', () => {
    hideContextMenu();
    openSettingsModal();
  });

  menuQuit.addEventListener('click', () => {
    window.electronAPI.quitApp();
  });

  // AI Chat
  function openChatBox() {
    chatBox.classList.remove('hidden');
    chatInput.focus();
    showBubble("Anya đang nghe bạn nói nè... ✨", 2500);
  }

  function closeChatBox() {
    chatBox.classList.add('hidden');
    chatInput.value = '';
    chooseNextAIAction();
  }

  async function handleSendChat() {
    const text = chatInput.value.trim();
    if (!text) return;

    chatBox.classList.add('hidden');
    showBubble("Anya đang nghĩ... 🤔💭", 10000);
    setState(State.CLICKED);

    try {
      const res = await window.electronAPI.askGemini(text);
      if (res && res.reply) {
        showBubble(res.reply, 6000);
        playSound('cute_chirp.wav');
        spawnParticles(6);
      } else {
        showBubble("Anya không nghe rõ, bạn nói lại nha!", 3000);
      }
    } catch (e) {
      showBubble("Opps, Anya gặp lỗi kết nối rùi!", 3000);
    } finally {
      setTimeout(chooseNextAIAction, 4000);
    }
  }

  chatSendBtn.addEventListener('click', handleSendChat);
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleSendChat();
    if (e.key === 'Escape') closeChatBox();
  });

  // Settings Modal
  function openSettingsModal() {
    applyConfigUI();
    settingsModal.classList.remove('hidden');
  }

  function closeSettingsModal() {
    settingsModal.classList.add('hidden');
  }

  closeSettingsBtn.addEventListener('click', closeSettingsModal);

  scaleSlider.addEventListener('input', () => {
    const scale = parseInt(scaleSlider.value, 10) / 100;
    scaleValue.textContent = `${scaleSlider.value}%`;
    petSpriteWrapper.style.transform = `scale(${scale})`;
  });

  speedSlider.addEventListener('input', () => {
    speedValue.textContent = `${speedSlider.value}`;
  });

  saveSettingsBtn.addEventListener('click', async () => {
    const newConfig = {
      scale: parseInt(scaleSlider.value, 10) / 100,
      speed: parseInt(speedSlider.value, 10),
      gemini_api_key: apiKeyInput.value.trim()
    };
    config = { ...config, ...newConfig };
    await window.electronAPI.saveConfig(config);
    closeSettingsModal();
    showBubble("Đã lưu cài đặt thành công! ✨", 2500);
    playSound('happy_jingle.wav');
  });

  // IPC Menu Commands from Tray
  if (window.electronAPI.onMenuCommand) {
    window.electronAPI.onMenuCommand((cmd) => {
      if (cmd === 'open-chat') openChatBox();
      if (cmd === 'open-settings') openSettingsModal();
      if (cmd === 'toggle-sound') {
        config.sound_enabled = !config.sound_enabled;
        window.electronAPI.saveConfig({ sound_enabled: config.sound_enabled });
        applyConfigUI();
      }
    });
  }

  // Initialize
  await initEngine();
  requestAnimationFrame(movementLoop);
  chooseNextAIAction();
  showBubble("Waku Waku! Bé Anya đã sẵn sàng! 🌸", 3500);
  playSound('waku_waku.wav');
  spawnParticles(8);
})();
