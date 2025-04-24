// src/renderer/App.jsx
import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileProcessingForm } from '@/components/FileProcessingForm';
import { RegexBuilder } from '@/components/RegexBuilder';

const App = () => {
  const [mode, setMode] = useState('rag');
  
  return (
    <div className="min-h-screen bg-background p-8">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold">🧠 Memory Forge</h1>
      </header>

      <Tabs defaultValue={mode} onValueChange={setMode} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="rag">RAG Memory</TabsTrigger>
          <TabsTrigger value="sft">SFT Data</TabsTrigger>
          <TabsTrigger value="regex">Regex Builder</TabsTrigger>
        </TabsList>

        <TabsContent value="rag">
          <FileProcessingForm mode="rag" />
        </TabsContent>

        <TabsContent value="sft">
          <FileProcessingForm mode="sft" />
        </TabsContent>

        <TabsContent value="regex">
          <RegexBuilder />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default App;