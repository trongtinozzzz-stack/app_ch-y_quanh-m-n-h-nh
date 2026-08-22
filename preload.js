const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Ultra-fast 0-latency 1-way position updates
  setPosFast: (x, y) => ipcRenderer.send('set-pos-fast', { x, y }),
  movePosFast: (dx, dy) => ipcRenderer.send('move-pos-fast', { dx, dy }),

  // Standard IPC
  moveWindow: (dx, dy) => ipcRenderer.invoke('move-window', { dx, dy }),
  setWindowPosition: (x, y) => ipcRenderer.invoke('set-window-position', { x, y }),
  getWindowPosition: () => ipcRenderer.invoke('get-window-position'),
  getScreenBounds: () => ipcRenderer.invoke('get-screen-bounds'),
  openImageDialog: () => ipcRenderer.invoke('open-image-dialog'),
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),
  askGemini: (prompt) => ipcRenderer.invoke('ask-gemini', prompt),
  quitApp: () => ipcRenderer.invoke('quit-app'),
  setIgnoreMouseEvents: (ignore, options) => ipcRenderer.invoke('set-ignore-mouse-events', ignore, options),
  onMenuCommand: (callback) => ipcRenderer.on('menu-command', (_event, value) => callback(value)),
  onScreenChanged: (callback) => ipcRenderer.on('screen-changed', (_event, value) => callback(value))
});
