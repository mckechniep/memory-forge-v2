// src/preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openFile: () => ipcRenderer.invoke('dialog:openFile'),
  processTranscript: (filePath, title, instruction, mode) => 
    ipcRenderer.invoke('process-transcript', filePath, title, instruction, mode),
  transcribeAudio: (filePath, title, instruction, mode) =>
    ipcRenderer.invoke('transcribe-audio', filePath, title, instruction, mode),
  // Regex dictionary functions
  saveRegexDictionary: (dictionary) => 
    ipcRenderer.invoke('regex:save', dictionary),
  loadRegexDictionary: () => 
    ipcRenderer.invoke('regex:load')
});
