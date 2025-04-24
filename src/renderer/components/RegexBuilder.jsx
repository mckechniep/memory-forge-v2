// src/renderer/components/RegexBuilder.jsx
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";

export const RegexBuilder = () => {
  const [dictionary, setDictionary] = useState({});
  const [displayDictionary, setDisplayDictionary] = useState('');
  const [category, setCategory] = useState('');
  const [words, setWords] = useState('');
  const [regex, setRegex] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadDictionary();
  }, []);

  const loadDictionary = async () => {
    try {
      const loadedDict = await window.electronAPI.loadRegexDictionary();
      setDictionary(loadedDict);
      updateDisplayDictionary(loadedDict);
    } catch (error) {
      setMessage('Error loading dictionary: ' + error.message);
    }
  };

  const generateRegex = () => {
    const wordArray = words.split(',').map(word => word.trim()).filter(word => word !== '');
    const regexPattern = wordArray.length > 0 ? `\\b(${wordArray.map(word => word).join('|')})\\b` : '';
    setRegex(regexPattern);
  };

  const updateDisplayDictionary = (dict) => {
    let pythonDict = "{\n";
    Object.entries(dict).forEach(([category, patterns]) => {
      pythonDict += `  "${category}": [\n`;
      if (Array.isArray(patterns)) {
        patterns.forEach((pattern, index) => {
          pythonDict += `    r"${pattern}"${index < patterns.length - 1 ? ',' : ''}\n`;
        });
      } else {
        Object.entries(patterns).forEach(([subcat, subpatterns], idx, arr) => {
          pythonDict += `    "${subcat}": [\n`;
          subpatterns.forEach((pattern, index) => {
            pythonDict += `      r"${pattern}"${index < subpatterns.length - 1 ? ',' : ''}\n`;
          });
          pythonDict += `    ]${idx < arr.length - 1 ? ',' : ''}\n`;
        });
      }
      pythonDict += `  ],\n`;
    });
    pythonDict += "}";
    setDisplayDictionary(pythonDict);
  };

  const handleAddToDictionary = () => {
    if (!category || !regex) return;

    const updatedDictionary = { ...dictionary };
    const categoryParts = category.split('.');

    if (categoryParts.length === 1) {
      if (!updatedDictionary[category]) {
        updatedDictionary[category] = [];
      }
      if (!updatedDictionary[category].includes(regex)) {
        updatedDictionary[category] = [...updatedDictionary[category], regex];
      }
    } else {
      const [mainCat, subCat] = categoryParts;
      if (!updatedDictionary[mainCat]) {
        updatedDictionary[mainCat] = {};
      }
      if (typeof updatedDictionary[mainCat] !== 'object') {
        updatedDictionary[mainCat] = {};
      }
      if (!updatedDictionary[mainCat][subCat]) {
        updatedDictionary[mainCat][subCat] = [];
      }
      if (!updatedDictionary[mainCat][subCat].includes(regex)) {
        updatedDictionary[mainCat][subCat] = [...updatedDictionary[mainCat][subCat], regex];
      }
    }

    setDictionary(updatedDictionary);
    updateDisplayDictionary(updatedDictionary);
  };

  const handleSaveDictionary = async () => {
    try {
      const result = await window.electronAPI.saveRegexDictionary(dictionary);
      setMessage(result.message);
    } catch (error) {
      setMessage('Error saving dictionary: ' + error.message);
    }
  };

  const handleResetDictionary = () => {
    setDictionary({});
    setDisplayDictionary('');
    setCategory('');
    setWords('');
    setRegex('');
  };

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Regex Pattern Builder</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="category">Category</Label>
            <Input
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="e.g., emotions.positive or activities"
            />
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="words">Matching Words/Phrases</Label>
            <Textarea
              id="words"
              placeholder="happy, joy, excited"
              value={words}
              onChange={(e) => setWords(e.target.value)}
            />
          </div>
          
          <Button onClick={generateRegex}>Generate Regex</Button>
          
          {regex && (
            <div className="grid gap-2">
              <Label>Generated Regex</Label>
              <Input readOnly value={regex ? `r"${regex}"` : ''} />
              <Button onClick={handleAddToDictionary}>Add to Dictionary</Button>
            </div>
          )}
        </CardContent>
      </Card>

      {message && (
        <Alert>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      {displayDictionary && (
        <Card>
          <CardHeader>
            <CardTitle>Current Dictionary</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="whitespace-pre-wrap bg-muted p-4 rounded-lg overflow-auto max-h-[400px]">
              {displayDictionary}
            </pre>
            <div className="flex gap-4 mt-4">
              <Button onClick={handleSaveDictionary}>
                Save Dictionary
              </Button>
              <Button variant="destructive" onClick={handleResetDictionary}>
                Reset Dictionary
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};