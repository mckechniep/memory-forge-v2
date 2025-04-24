// src/preload.js
const { contextBridge, ipcRenderer } = require('electron');
// import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  openFile: () => ipcRenderer.invoke('dialog:openFile'),
  processTranscript: (filePath, title, instruction, mode) => 
    ipcRenderer.invoke('process-transcript', filePath, title, instruction, mode),
  transcribeAudio: (filePath, title, instruction, mode) =>
    ipcRenderer.invoke('transcribe-audio', filePath, title, instruction, mode)
});