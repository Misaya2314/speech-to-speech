const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const isDev = process.env.NODE_ENV === 'development';
const fs = require('fs');
const http = require('http');

// 保持对窗口对象的全局引用，避免 JavaScript 垃圾回收时窗口被关闭
let mainWindow;

// 添加错误捕获
process.on('uncaughtException', (error) => {
  console.error('未捕获的异常:', error);
});

// 检查URL是否可用
function checkUrlAvailable(url) {
  return new Promise((resolve) => {
    const request = http.get(url, (response) => {
      if (response.statusCode === 200) {
        resolve(true);
      } else {
        resolve(false);
      }
      response.resume(); // 消费响应数据以释放内存
    });
    
    request.on('error', () => {
      resolve(false);
    });
    
    request.setTimeout(1000, () => {
      request.abort();
      resolve(false);
    });
  });
}

function createWindow() {
  console.log('正在创建主窗口...');
  console.log('开发模式:', isDev);
  
  // 创建浏览器窗口
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    },
    icon: path.join(process.cwd(), 'public', 'icon.ico')
  });

  // 加载应用
  if (isDev) {
    // 开发环境下，加载 Vite 开发服务器
    (async () => {
      const viteUrl = 'http://localhost:3210/';
      
      // 检查Vite开发服务器是否已启动
      const isViteRunning = await checkUrlAvailable(viteUrl);
      
      if (isViteRunning) {
        console.log('正在加载开发服务器URL:', viteUrl);
        try {
          await mainWindow.loadURL(viteUrl);
          console.log('成功加载开发服务器');
        } catch (err) {
          console.error('加载开发服务器失败:', err);
        }
      } else {
        console.error('Vite开发服务器未运行，请先启动npm run dev');
        // 显示错误页面
        mainWindow.loadFile(path.join(__dirname, 'error.html')).catch(err => {
          console.error('加载错误页面失败:', err);
        });
      }
      
      // 打开开发者工具
      mainWindow.webContents.openDevTools();
    })();
  } else {
    // 生产环境下，加载打包后的应用
    const filePath = path.join(__dirname, '../dist/index.html');
    console.log('正在加载本地文件:', filePath);
    
    if (fs.existsSync(filePath)) {
      mainWindow.loadFile(filePath).catch(err => {
        console.error('加载本地文件失败:', err);
      });
    } else {
      console.error('文件不存在:', filePath);
    }
  }

  // 窗口关闭时触发
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
  
  // 监听页面加载完成事件
  mainWindow.webContents.on('did-finish-load', () => {
    console.log('页面加载完成');
  });
  
  // 监听页面加载失败事件
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error('页面加载失败:', errorCode, errorDescription);
  });
}

// 当 Electron 完成初始化时被调用
app.whenReady().then(() => {
  console.log('Electron 应用初始化完成');
  createWindow();

  app.on('activate', () => {
    // 在 macOS 上点击 dock 图标时没有已打开的窗口则重新创建一个窗口
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
}).catch(err => {
  console.error('Electron 初始化失败:', err);
});

// 关闭所有窗口时退出应用，除了 macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC 事件处理
// 连接到后端 WebSocket 服务器
ipcMain.handle('connect-backend', async (event, options) => {
  try {
    console.log('收到连接后端请求:', options);
    // 这里我们只需将消息转发给渲染进程
    // 实际的 WebSocket 连接将在渲染进程中处理
    if (mainWindow) {
      mainWindow.webContents.send('backend-connect-request', options);
    }
    return { success: true };
  } catch (error) {
    console.error('Failed to connect to backend:', error);
    return { success: false, error: error.message };
  }
});

// 断开后端连接
ipcMain.handle('disconnect-backend', async () => {
  try {
    console.log('收到断开后端请求');
    if (mainWindow) {
      mainWindow.webContents.send('backend-disconnect-request');
    }
    return { success: true };
  } catch (error) {
    console.error('Failed to disconnect from backend:', error);
    return { success: false, error: error.message };
  }
}); 