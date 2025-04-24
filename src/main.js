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

                // Convert Python dictionary to JavaScript object directly
                // This is safer than trying to parse it as JSON
                const pythonToJs = (pythonCode) => {
                    // Create a clean JavaScript object
                    let result = {};
                    
                    // Remove outer braces and split by top-level commas
                    const content = pythonCode.trim().slice(1, -1).trim();
                    
                    // Parse each key-value pair
                    let depth = 0;
                    let currentKey = '';
                    let currentValue = '';
                    let inKey = true;
                    
                    for (let i = 0; i < content.length; i++) {
                        const char = content[i];
                        
                        // Track nesting depth
                        if (char === '{' || char === '[') depth++;
                        else if (char === '}' || char === ']') depth--;
                        
                        // At top level, look for key-value separators
                        if (depth === 0 && char === ':' && inKey) {
                            currentKey = currentKey.trim().replace(/^['"](.*)['"]$/, '$1');
                            inKey = false;
                            continue;
                        }
                        
                        // At top level, look for pair separators
                        if (depth === 0 && char === ',' && !inKey) {
                            // Process the value
                            currentValue = currentValue.trim();
                            
                            // Handle different value types
                            if (currentValue === 'True') result[currentKey] = true;
                            else if (currentValue === 'False') result[currentKey] = false;
                            else if (currentValue === 'None') result[currentKey] = null;
                            else if (currentValue.startsWith('[') && currentValue.endsWith(']')) {
                                // Handle arrays
                                const arrayContent = currentValue.slice(1, -1).trim();
                                const items = [];
                                
                                // Parse array items
                                let itemStart = 0;
                                let itemDepth = 0;
                                
                                for (let j = 0; j <= arrayContent.length; j++) {
                                    const itemChar = j < arrayContent.length ? arrayContent[j] : ',';
                                    
                                    if (itemChar === '{' || itemChar === '[') itemDepth++;
                                    else if (itemChar === '}' || itemChar === ']') itemDepth--;
                                    
                                    if ((itemDepth === 0 && itemChar === ',') || j === arrayContent.length) {
                                        let item = arrayContent.slice(itemStart, j).trim();
                                        
                                        // Handle raw strings and quotes
                                        if (item.startsWith('r"') && item.endsWith('"')) {
                                            item = item.slice(2, -1);
                                        } else if ((item.startsWith('"') && item.endsWith('"')) || 
                                                 (item.startsWith("'") && item.endsWith("'"))) {
                                            item = item.slice(1, -1);
                                        }
                                        
                                        if (item) items.push(item);
                                        itemStart = j + 1;
                                    }
                                }
                                
                                result[currentKey] = items;
                            } else if ((currentValue.startsWith('"') && currentValue.endsWith('"')) || 
                                      (currentValue.startsWith("'") && currentValue.endsWith("'"))) {
                                // Handle strings
                                result[currentKey] = currentValue.slice(1, -1);
                            } else if (currentValue.startsWith('r"') && currentValue.endsWith('"')) {
                                // Handle raw strings
                                result[currentKey] = currentValue.slice(2, -1);
                            } else {
                                // Try to parse as number or keep as string
                                const num = parseFloat(currentValue);
                                result[currentKey] = isNaN(num) ? currentValue : num;
                            }
                            
                            // Reset for next pair
                            currentKey = '';
                            currentValue = '';
                            inKey = true;
                            continue;
                        }
                        
                        // Accumulate characters
                        if (inKey) currentKey += char;
                        else currentValue += char;
                    }
                    
                    // Handle the last pair if there's no trailing comma
                    if (currentKey && !inKey) {
                        currentValue = currentValue.trim();
                        
                        if (currentValue === 'True') result[currentKey] = true;
                        else if (currentValue === 'False') result[currentKey] = false;
                        else if (currentValue === 'None') result[currentKey] = null;
                        else if (currentValue.startsWith('[') && currentValue.endsWith(']')) {
                            // Handle arrays (simplified for the last item)
                            const arrayContent = currentValue.slice(1, -1).trim();
                            const items = arrayContent.split(',')
                                .map(item => {
                                    item = item.trim();
                                    if (item.startsWith('r"') && item.endsWith('"')) {
                                        return item.slice(2, -1);
                                    } else if ((item.startsWith('"') && item.endsWith('"')) || 
                                             (item.startsWith("'") && item.endsWith("'"))) {
                                        return item.slice(1, -1);
                                    }
                                    return item;
                                })
                                .filter(item => item);
                            
                            result[currentKey] = items;
                        } else if ((currentValue.startsWith('"') && currentValue.endsWith('"')) || 
                                  (currentValue.startsWith("'") && currentValue.endsWith("'"))) {
                            result[currentKey] = currentValue.slice(1, -1);
                        } else if (currentValue.startsWith('r"') && currentValue.endsWith('"')) {
                            result[currentKey] = currentValue.slice(2, -1);
                        } else {
                            const num = parseFloat(currentValue);
                            result[currentKey] = isNaN(num) ? currentValue : num;
                        }
                    }
                    
                    return result;
                };
                
                const dictionary = pythonToJs(dictionaryString);
                
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

// Update the regex:save handler to properly format Python raw strings
ipcMain.handle('regex:save', async (event, dictionary) => {
    try {
        // Save the JSON version
        await fs.writeFile(regexDictionaryPath, JSON.stringify(dictionary, null, 2));
        
        // Convert to Python format for process.py
        const processFilePath = path.join(__dirname, '..', 'backend', 'process.py');
        let processContent = await fs.readFile(processFilePath, 'utf8');
        
        // Find the regex_tag_patterns dictionary in the file
        const regexDictStart = processContent.indexOf('regex_tag_patterns = {');
        const regexDictEnd = processContent.indexOf('# Clean the text', regexDictStart);
        
        if (regexDictStart !== -1 && regexDictEnd !== -1) {
            // Helper function to format Python lists
            const formatPythonList = (arr) => {
                return arr.map(item => {
                    if (typeof item === 'string') {
                        return `r"${item}"`;
                    }
                    return item;
                });
            };

            // Convert JSON to Python format
            let pythonDict = JSON.stringify(dictionary, (key, value) => {
                if (Array.isArray(value)) {
                    return formatPythonList(value);
                }
                return value;
            }, 4)
                .replace(/"([^"]+)":/g, '$1:') // Remove quotes from keys
                .replace(/: "r"/g, ': r"') // Fix double quoted r prefix
                .replace(/true/g, 'True')
                .replace(/false/g, 'False')
                .replace(/null/g, 'None');
            
            // Replace the dictionary content while preserving the rest of the file
            const newContent = processContent.slice(0, regexDictStart) +
                'regex_tag_patterns = ' + pythonDict + '\n\n' +
                processContent.slice(regexDictEnd);
            
            await fs.writeFile(processFilePath, newContent, 'utf8');
            return { success: true, message: 'Regex dictionary saved successfully' };
        }
        
        return { success: false, message: 'Could not locate regex dictionary in process.py' };
    } catch (error) {
        console.error('Error saving regex dictionary:', error);
        return { success: false, message: error.message };
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
