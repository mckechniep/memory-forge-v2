// src/renderer/App.jsx
import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RegexBuilder } from '@/components/RegexBuilder';

const App = () => {
  const [mode, setMode] = useState('rag');
  
  return (
    <div className="min-h-screen bg-background p-8">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold">🧠 Memory Forge</h1>
      </header>

      <Tabs defaultValue={mode} onValueChange={setMode} className="space-y-6">
        <TabsList>
          <TabsTrigger value="rag">RAG Memory</TabsTrigger>
          <TabsTrigger value="sft">SFT Data</TabsTrigger>
        </TabsList>

        <TabsContent value="rag">
          {/* RAG memory form will go here */}
        </TabsContent>

        <TabsContent value="sft">
          {/* SFT data form will go here */}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default App;