// src/main.js
const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs').promises;

// Store default directories
let defaultOpenDirectory = app.getPath("documents");
let defaultSaveDirectory = app.getPath("documents");
const regexDictionaryPath = path.join(app.getPath("userData"), "regex_dictionary.json");

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // In development, load from Vite dev server
  if (process.env.NODE_ENV === 'development') {
    win.loadURL('http://localhost:5173');
    win.webContents.openDevTools();
  } else {
    win.loadFile('dist/index.html');
  }
}

app.whenReady().then(() => {
  createWindow();

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

// File handling IPC endpoints
ipcMain.handle('dialog:openFile', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    defaultPath: defaultOpenDirectory,
    properties: ['openFile'],
    filters: [
      { name: 'All Supported Files', extensions: ['txt', 'mp3', 'wav', 'ogg', 'm4a'] },
      { name: 'Text Files', extensions: ['txt'] },
      { name: 'Audio Files', extensions: ['mp3', 'wav', 'ogg', 'm4a'] }
    ]
  });

  if (canceled || filePaths.length === 0) {
    return null;
  }

  defaultOpenDirectory = path.dirname(filePaths[0]);
  return filePaths[0];
});

// Add regex dictionary handlers
ipcMain.handle('regex:save', async (event, dictionary) => {
    try {
      await fs.writeFile(regexDictionaryPath, JSON.stringify(dictionary, null, 2));
      // Also update process.py with the new dictionary
      const processFilePath = path.join(__dirname, '..', 'backend', 'process.py');
      let processContent = await fs.readFile(processFilePath, 'utf8');
      
      // Find the regex_tag_patterns dictionary in the file
      const regexDictStart = processContent.indexOf('regex_tag_patterns = {');
      const regexDictEnd = processContent.indexOf('# Clean the text', regexDictStart);
      
      if (regexDictStart !== -1 && regexDictEnd !== -1) {
        // Replace the dictionary content while preserving the rest of the file
        const newContent = processContent.slice(0, regexDictStart) +
          'regex_tag_patterns = ' + JSON.stringify(dictionary, null, 4) + '\n\n' +
          processContent.slice(regexDictEnd);
        
        await fs.writeFile(processFilePath, newContent, 'utf8');
        return { success: true, message: 'Regex dictionary saved successfully' };
      }
      
      return { success: false, message: 'Could not locate regex dictionary in process.py' };
    } catch (error) {
      return { success: false, message: error.message };
    }
});

ipcMain.handle('regex:load', async () => {
    try {
      const data = await fs.readFile(regexDictionaryPath, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      // If the file doesn't exist or there's an error, load from process.py
      try {
        const processFilePath = path.join(__dirname, '..', 'backend', 'process.py');
        const processContent = await fs.readFile(processFilePath, 'utf8');
        
        // Extract the regex dictionary from process.py
        const regexDictStart = processContent.indexOf('regex_tag_patterns = {');
        const regexDictEnd = processContent.indexOf('# Clean the text', regexDictStart);
        
        if (regexDictStart !== -1 && regexDictEnd !== -1) {
          const dictionaryString = processContent
            .slice(regexDictStart + 'regex_tag_patterns = '.length, regexDictEnd)
            .trim();
          
          // Convert Python dictionary to JavaScript object
          const dictionary = eval('(' + dictionaryString.replace(/'/g, '"') + ')');
          
          // Save it to the user data directory for future use
          await fs.writeFile(regexDictionaryPath, JSON.stringify(dictionary, null, 2));
          
          return dictionary;
        }
        
        return {};
      } catch (err) {
        console.error('Error loading regex dictionary:', err);
        return {};
      }
    }
});

// Process files IPC endpoints
ipcMain.handle('process-transcript', async (event, filePath, title, instruction, mode) => {
  const saveDialog = await dialog.showSaveDialog({
    defaultPath: path.join(defaultSaveDirectory, `${title.replace(/\s+/g, '_')}.jsonl`),
    filters: [{ name: 'JSONL', extensions: ['jsonl'] }]
  });

  if (saveDialog.canceled || !saveDialog.filePath) {
    return 'Save canceled.';
  }

  defaultSaveDirectory = path.dirname(saveDialog.filePath);
  return runPython('process.py', [filePath, title, instruction, mode, saveDialog.filePath]);
});

ipcMain.handle('transcribe-audio', async (event, filePath, title, instruction, mode) => {
  if (!filePath) {
    return 'Error: No valid file path provided';
  }

  const saveDialog = await dialog.showSaveDialog({
    defaultPath: path.join(defaultSaveDirectory, `${title.replace(/\s+/g, '_')}.jsonl`),
    filters: [{ name: 'JSONL', extensions: ['jsonl'] }]
  });

  if (saveDialog.canceled || !saveDialog.filePath) {
    return 'Save canceled.';
  }

  defaultSaveDirectory = path.dirname(saveDialog.filePath);
  return runPython('transcribe.py', [filePath, title, instruction, mode, saveDialog.filePath]);
});

function runPython(scriptName, args) {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(__dirname, '..', 'backend', scriptName);
    const venvPython = process.platform === 'win32'
      ? path.join(__dirname, '..', 'backend', 'venv', 'Scripts', 'python.exe')
      : path.join(__dirname, '..', 'backend', 'venv', 'bin', 'python');

    const subprocess = spawn(venvPython, [scriptPath, ...args.map(arg => path.normalize(arg))], {
      cwd: path.join(__dirname, '..', 'backend')
    });

    let output = '';
    let errorOutput = '';

    subprocess.stdout.on('data', data => output += data.toString());
    subprocess.stderr.on('data', data => errorOutput += data.toString());

    subprocess.on('close', code => {
      if (code === 0) resolve(output.trim());
      else reject(errorOutput || `Script exited with code ${code}`);
    });
  });
}
