// src/renderer/components/FileProcessingForm.jsx
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export const FileProcessingForm = ({ mode }) => {
  const [title, setTitle] = useState('');
  const [instruction, setInstruction] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [output, setOutput] = useState('');
  const [processing, setProcessing] = useState(false);

  const handleFileSelect = async () => {
    try {
      const filePath = await window.electronAPI.openFile();
      if (filePath) {
        setSelectedFile(filePath);
      }
    } catch (error) {
      console.error('Error selecting file:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile || !title) return;

    setProcessing(true);
    try {
      // Check file extension to determine if it's an audio file
      const isAudio = /\.(mp3|wav|ogg|m4a)$/i.test(selectedFile);
      const result = isAudio
        ? await window.electronAPI.transcribeAudio(selectedFile, title, instruction, mode)
        : await window.electronAPI.processTranscript(selectedFile, title, instruction, mode);
      
      setOutput(result);
    } catch (error) {
      setOutput(`Error: ${error.message}`);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{mode === 'rag' ? 'RAG Memory Creation' : 'SFT Data Creation'}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label>Title</Label>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter a title..."
          />
        </div>

        <div className="space-y-2">
          <Label>Instruction (optional)</Label>
          <Textarea
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            placeholder="Enter processing instructions..."
          />
        </div>

        <div className="space-y-2">
          <Label>File</Label>
          <div className="flex gap-2">
            <Input
              readOnly
              value={selectedFile || ''}
              placeholder="Select a file..."
            />
            <Button onClick={handleFileSelect}>Browse</Button>
          </div>
        </div>

        <Button 
          onClick={handleSubmit}
          disabled={!selectedFile || !title || processing}
          className="w-full"
        >
          {processing ? 'Processing...' : 'Process File'}
        </Button>

        {output && (
          <div className="mt-4">
            <Label>Output</Label>
            <Textarea
              readOnly
              value={output}
              className="min-h-[200px] font-mono text-sm"
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
};