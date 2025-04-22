import { BrowserWindow, ipcMain } from 'electron';

/**
 * 设置自定义标题栏功能
 * @param mainWindow 主窗口实例
 */
export function setupCustomTitlebar(mainWindow: BrowserWindow): void {
  // 设置窗口无边框
  if (mainWindow) {
    // 使用正确的API设置无边框
    mainWindow.setWindowButtonVisibility(false);
  }

  // 监听最小化按钮点击
  ipcMain.on('window-minimize', () => {
    if (mainWindow) {
      mainWindow.minimize();
    }
  });

  // 监听最大化/还原按钮点击
  ipcMain.on('window-maximize', () => {
    if (mainWindow) {
      if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
      } else {
        mainWindow.maximize();
      }
    }
  });

  // 监听关闭按钮点击
  ipcMain.on('window-close', () => {
    if (mainWindow) {
      mainWindow.close();
    }
  });
}

/**
 * 设置渲染进程中需要用到的窗口状态
 * @param mainWindow 主窗口实例
 */
export function setupWindowStateEvents(mainWindow: BrowserWindow): void {
  // 监听窗口最大化事件
  mainWindow.on('maximize', () => {
    mainWindow.webContents.send('window-maximized', true);
  });

  // 监听窗口还原事件
  mainWindow.on('unmaximize', () => {
    mainWindow.webContents.send('window-maximized', false);
  });
} 