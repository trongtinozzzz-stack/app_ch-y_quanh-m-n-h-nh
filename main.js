const { app, BrowserWindow, ipcMain, screen, Tray, Menu, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow = null;
let tray = null;
const CONFIG_PATH = path.join(__dirname, 'config.json');

function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      const data = fs.readFileSync(CONFIG_PATH, 'utf-8');
      return JSON.parse(data);
    }
  } catch (err) {
    console.error('Error loading config.json:', err);
  }
  return {
    gemini_api_key: "",
    sound_enabled: true,
    scale: 1.0,
    speed: 3
  };
}

function saveConfig(newConfig) {
  try {
    const current = loadConfig();
    const merged = { ...current, ...newConfig };
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(merged, null, 2), 'utf-8');
    return true;
  } catch (err) {
    console.error('Error saving config.json:', err);
    return false;
  }
}

function createWindow() {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;
  const { x: screenX, y: screenY } = primaryDisplay.workArea;

  const petWidth = 200;
  const petHeight = 220;
  const initialX = Math.round(screenX + screenWidth - petWidth - 100);
  const initialY = Math.round(screenY + screenHeight - petHeight);

  mainWindow = new BrowserWindow({
    width: petWidth,
    height: petHeight,
    x: initialX,
    y: initialY,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    resizable: false,
    hasShadow: false,
    skipTaskbar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      backgroundThrottling: false
    }
  });

  mainWindow.setAlwaysOnTop(true, 'screen-saver');
  mainWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });

  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  screen.on('display-metrics-changed', () => {
    if (mainWindow) {
      const display = screen.getDisplayMatching(mainWindow.getBounds());
      mainWindow.webContents.send('screen-changed', display.workArea);
    }
  });
}

function createTray() {
  const iconPath = path.join(__dirname, 'assets', 'icon.png');
  if (fs.existsSync(iconPath)) {
    tray = new Tray(iconPath);
  } else {
    tray = new Tray(path.join(__dirname, 'assets', 'sprites', 'clicked.png'));
  }

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Desktop Pet Anya 🎀',
      enabled: false
    },
    { type: 'separator' },
    {
      label: '🔄 Đặt lại vị trí ban đầu',
      click: () => {
        if (mainWindow) {
          const primaryDisplay = screen.getPrimaryDisplay();
          const { width, height } = primaryDisplay.workAreaSize;
          const { x, y } = primaryDisplay.workArea;
          mainWindow.setPosition(x + width - 220, y + height - 220);
        }
      }
    },
    {
      label: '✨ Trò chuyện với Anya (Gemini AI)',
      click: () => {
        if (mainWindow) {
          mainWindow.webContents.send('menu-command', 'open-chat');
        }
      }
    },
    {
      label: '⚙️ Bảng cài đặt',
      click: () => {
        if (mainWindow) {
          mainWindow.webContents.send('menu-command', 'open-settings');
        }
      }
    },
    {
      label: '🔊 Bật/Tắt âm thanh',
      click: () => {
        if (mainWindow) {
          mainWindow.webContents.send('menu-command', 'toggle-sound');
        }
      }
    },
    { type: 'separator' },
    {
      label: '❌ Thoát',
      click: () => {
        app.quit();
      }
    }
  ]);

  tray.setToolTip('Desktop Pet Mascot 🎀');
  tray.setContextMenu(contextMenu);
  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

// Fast 0-latency position updates
ipcMain.on('set-pos-fast', (_event, { x, y }) => {
  if (mainWindow) {
    mainWindow.setPosition(Math.round(x), Math.round(y));
  }
});

ipcMain.on('move-pos-fast', (_event, { dx, dy }) => {
  if (mainWindow) {
    const [curX, curY] = mainWindow.getPosition();
    mainWindow.setPosition(Math.round(curX + dx), Math.round(curY + dy));
  }
});

// IPC Handlers
ipcMain.handle('get-screen-bounds', () => {
  if (!mainWindow) return { x: 0, y: 0, width: 1920, height: 1080 };
  const currentDisplay = screen.getDisplayMatching(mainWindow.getBounds());
  return currentDisplay.workArea;
});

ipcMain.handle('get-window-position', () => {
  if (!mainWindow) return { x: 0, y: 0, width: 200, height: 220 };
  const bounds = mainWindow.getBounds();
  return bounds;
});

ipcMain.handle('set-window-position', (event, { x, y }) => {
  if (mainWindow) {
    mainWindow.setPosition(Math.round(x), Math.round(y));
  }
});

ipcMain.handle('move-window', (event, { dx, dy }) => {
  if (mainWindow) {
    const [curX, curY] = mainWindow.getPosition();
    mainWindow.setPosition(Math.round(curX + dx), Math.round(curY + dy));
  }
});

ipcMain.handle('set-ignore-mouse-events', (event, ignore, options) => {
  if (mainWindow) {
    mainWindow.setIgnoreMouseEvents(ignore, options || {});
  }
});

ipcMain.handle('get-config', () => {
  return loadConfig();
});

ipcMain.handle('save-config', (event, newConfig) => {
  return saveConfig(newConfig);
});

ipcMain.handle('open-image-dialog', async () => {
  if (!mainWindow) return null;
  const result = await dialog.showOpenDialog(mainWindow, {
    title: 'Chọn ảnh avatar cho Pet',
    properties: ['openFile'],
    filters: [
      { name: 'Hình ảnh', extensions: ['png', 'jpg', 'jpeg', 'webp', 'gif'] }
    ]
  });

  if (!result.canceled && result.filePaths.length > 0) {
    const filePath = result.filePaths[0];
    const data = fs.readFileSync(filePath);
    const base64 = `data:image/${path.extname(filePath).slice(1)};base64,${data.toString('base64')}`;
    return { filePath, dataUrl: base64 };
  }
  return null;
});

ipcMain.handle('ask-gemini', async (event, userPrompt) => {
  const config = loadConfig();
  const apiKey = config.gemini_api_key;
  if (!apiKey) {
    return {
      success: false,
      reply: "Hehe, bạn chưa thêm Gemini API key vào config.json kìa! Hãy mở cài đặt để nhập key nhé 🌸"
    };
  }

  try {
    const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;
    const systemInstruction = "Bạn là cô bé Anya Forger dễ thương, đáng yêu trong Spy x Family. Bạn đang làm thú cưng desktop pet chạy loanh quanh trên màn hình máy tính của người dùng. Hãy trả lời ngắn gọn (1-2 câu), vui vẻ, dùng icon dễ thương, thỉnh thoảng nói 'Waku waku!', 'Hehe' bằng tiếng Việt.";

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        contents: [
          {
            role: "user",
            parts: [{ text: `${systemInstruction}\n\nNgười dùng nói với Anya: "${userPrompt}"` }]
          }
        ],
        generationConfig: {
          maxOutputTokens: 150,
          temperature: 0.8
        }
      })
    });

    const data = await response.json();
    if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
      const replyText = data.candidates[0].content.parts[0].text.trim();
      return { success: true, reply: replyText };
    } else if (data.error) {
      return { success: false, reply: `Lỗi Gemini: ${data.error.message || 'Không thể kết nối'}` };
    }
    return { success: false, reply: "Anya đang bận ăn đậu phộng rùi, thử lại nhé!" };
  } catch (err) {
    console.error('Error calling Gemini API:', err);
    return { success: false, reply: "Waku waku! Có chút trục trặc mạng rùi nha!" };
  }
});

ipcMain.handle('quit-app', () => {
  app.quit();
});

// App lifecycle
app.whenReady().then(() => {
  createWindow();
  createTray();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
