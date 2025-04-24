import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { CustomDialog } from './CustomDialog';

export const RegexBuilder = () => {
  const [dictionary, setDictionary] = useState({});
  const [displayDictionary, setDisplayDictionary] = useState('');
  const [category, setCategory] = useState('');
  const [subcategory, setSubcategory] = useState('');
  const [words, setWords] = useState('');
  const [regex, setRegex] = useState('');
  const [message, setMessage] = useState('');
  const [categories, setCategories] = useState([]);
  const [subcategories, setSubcategories] = useState([]);
  const [showCategoryDialog, setShowCategoryDialog] = useState(false);
  const [showSubcategoryDialog, setShowSubcategoryDialog] = useState(false);

  useEffect(() => {
    loadDictionary();
  }, []);

  useEffect(() => {
    if (dictionary) {
      setCategories(Object.keys(dictionary));
    }
  }, [dictionary]);

  useEffect(() => {
    if (category && dictionary[category]) {
      const subCats = typeof dictionary[category] === 'object' && !Array.isArray(dictionary[category])
        ? Object.keys(dictionary[category])
        : [];
      setSubcategories(subCats);
    } else {
      setSubcategories([]);
    }
  }, [category, dictionary]);

  const loadDictionary = async () => {
    try {
      console.log('Loading dictionary...');
      const loadedDict = await window.electronAPI.loadRegexDictionary();
      console.log('Dictionary loaded:', loadedDict);
      
      if (loadedDict && typeof loadedDict === 'object') {
        setDictionary(loadedDict);
        updateDisplayDictionary(loadedDict);
        const cats = Object.keys(loadedDict);
        console.log('Setting categories:', cats);
        setCategories(cats);
      } else {
        console.warn('Dictionary loaded but was empty or invalid format');
        setDictionary({});
        updateDisplayDictionary({});
        setCategories([]);
        setMessage('Dictionary loaded but was empty or invalid format');
      }
    } catch (error) {
      console.error('Error loading dictionary:', error);
      setMessage('Error loading dictionary: ' + (error.message || 'Unknown error'));
      setDictionary({});
      updateDisplayDictionary({});
      setCategories([]);
    }
  };

  const generateRegex = () => {
    const wordArray = words
      .split(',')
      .map(word => word.trim())
      .filter(word => word !== '');

    if (wordArray.length > 0) {
      const escapedWords = wordArray.map(word => 
        word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      );
      const regexPattern = `\\b(${escapedWords.join('|')})\\b`;
      setRegex(regexPattern);
    } else {
      setRegex('');
    }
  };

  const updateDisplayDictionary = (dict) => {
    if (!dict || typeof dict !== 'object') {
      setDisplayDictionary('{}');
      return;
    }
    
    try {
      let pythonDict = "{\n";
      Object.entries(dict).forEach(([category, patterns]) => {
        pythonDict += `  "${category}": {\n`;
        
        // Check if patterns is an array
        if (Array.isArray(patterns)) {
          pythonDict += `    "patterns": [\n`;
          patterns.forEach((pattern, index) => {
            pythonDict += `      r"${pattern}"${index < patterns.length - 1 ? ',' : ''}\n`;
          });
          pythonDict += "    ]\n";
        } 
        // Check if patterns is an object
        else if (patterns && typeof patterns === 'object') {
          const entries = Object.entries(patterns);
          entries.forEach(([subcat, subpatterns], idx) => {
            // Make sure subpatterns is an array
            if (!Array.isArray(subpatterns)) {
              subpatterns = [];
            }
            
            pythonDict += `    "${subcat}": [\n`;
            subpatterns.forEach((pattern, index) => {
              pythonDict += `      r"${pattern}"${index < subpatterns.length - 1 ? ',' : ''}\n`;
            });
            pythonDict += `    ]${idx < entries.length - 1 ? ',' : ''}\n`;
          });
        }
        // Handle unexpected data type
        else {
          pythonDict += `    "patterns": []\n`;
        }
        
        pythonDict += "  },\n";
      });
      pythonDict += "}";
      setDisplayDictionary(pythonDict);
    } catch (error) {
      console.error('Error formatting dictionary:', error);
      setDisplayDictionary('{}');
    }
  };

  const handleAddToDictionary = () => {
    if (!category || !regex) {
      setMessage('Please select a category and provide a regex pattern');
      return;
    }

    const updatedDictionary = { ...dictionary };
    if (!updatedDictionary[category]) {
      updatedDictionary[category] = {};
    }

    if (subcategory) {
      if (!updatedDictionary[category][subcategory]) {
        updatedDictionary[category][subcategory] = [];
      }
      if (!updatedDictionary[category][subcategory].includes(regex)) {
        updatedDictionary[category][subcategory] = [...updatedDictionary[category][subcategory], regex];
      }
    } else {
      if (Array.isArray(updatedDictionary[category])) {
        if (!updatedDictionary[category].includes(regex)) {
          updatedDictionary[category] = [...updatedDictionary[category], regex];
        }
      } else {
        updatedDictionary[category] = [regex];
      }
    }

    setDictionary(updatedDictionary);
    updateDisplayDictionary(updatedDictionary);
    setMessage('Pattern added successfully');
  };

  const handleSaveDictionary = async () => {
    try {
      const result = await window.electronAPI.saveRegexDictionary(dictionary);
      setMessage(result.message);
    } catch (error) {
      setMessage('Error saving dictionary: ' + error.message);
    }
  };

  const handleCreateNewCategory = () => {
    console.log('Opening category dialog...');
    setShowCategoryDialog(true);
  };

  const handleCategoryConfirm = (newCategory) => {
    console.log('New category name:', newCategory);
    if (newCategory && newCategory.trim() !== '') {
      if (!dictionary[newCategory]) {
        const updatedDictionary = {
          ...dictionary,
          [newCategory]: {}
        };
        console.log('Updated dictionary:', updatedDictionary);
        setDictionary(updatedDictionary);
        updateDisplayDictionary(updatedDictionary);
        setCategories(prevCategories => [...prevCategories, newCategory]);
        setCategory(newCategory);
        setMessage('New category created');
      } else {
        setMessage('Category already exists');
      }
    }
    setShowCategoryDialog(false);
  };

  const handleCreateNewSubcategory = () => {
    if (!category) {
      setMessage('Please select a category first');
      return;
    }
    setShowSubcategoryDialog(true);
  };

  const handleSubcategoryConfirm = (newSubcategory) => {
    if (newSubcategory && newSubcategory.trim() !== '') {
      const updatedDictionary = { ...dictionary };
      if (!updatedDictionary[category][newSubcategory]) {
        updatedDictionary[category][newSubcategory] = [];
        setDictionary(updatedDictionary);
        updateDisplayDictionary(updatedDictionary);
        setMessage('New subcategory created');
        setSubcategories([...subcategories, newSubcategory]);
        setSubcategory(newSubcategory);
      } else {
        setMessage('Subcategory already exists');
      }
    }
    setShowSubcategoryDialog(false);
  };

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Regex Pattern Builder</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="flex gap-4">
            <div className="flex-1">
                <Label>Category</Label>
                <div className="flex gap-2">
                  <Select value={category} onValueChange={setCategory}>
                    <SelectTrigger className="bg-background border-2 text-foreground font-medium">
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent className="bg-background border-2 text-foreground font-medium shadow-lg">
                      {categories.map(cat => (
                        <SelectItem key={cat} value={cat} className="hover:bg-muted">{cat}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button onClick={handleCreateNewCategory} variant="outline" type="button">New</Button>
                </div>
              </div>

            {subcategories.length > 0 && (
              <div className="flex-1">
                <Label>Subcategory</Label>
                <div className="flex gap-2">
                  <Select value={subcategory} onValueChange={setSubcategory}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select subcategory" />
                    </SelectTrigger>
                    <SelectContent>
                      {subcategories.map(subcat => (
                        <SelectItem key={subcat} value={subcat}>{subcat}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button onClick={handleCreateNewSubcategory} variant="outline">New</Button>
                </div>
              </div>
            )}
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="words">Words or Phrases (comma-separated)</Label>
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
              <Input readOnly value={regex} />
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
            <pre className="whitespace-pre-wrap bg-muted p-4 rounded-lg overflow-auto max-h-[400px] text-sm">
              {displayDictionary}
            </pre>
            <div className="flex gap-4 mt-4">
              <Button onClick={handleSaveDictionary}>
                Save Dictionary
              </Button>
              <Button 
                variant="destructive" 
                onClick={() => {
                  if (confirm('Are you sure you want to reset the dictionary?')) {
                    setDictionary({});
                    setDisplayDictionary('');
                    setCategory('');
                    setWords('');
                    setRegex('');
                  }
                }}
              >
                Reset Dictionary
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    <CustomDialog
      title="Create New Category"
      isOpen={showCategoryDialog}
      onClose={() => setShowCategoryDialog(false)}
      onConfirm={handleCategoryConfirm}
      inputLabel="Category Name"
      placeholder="Enter category name"
    />
    
    <CustomDialog
      title="Create New Subcategory"
      isOpen={showSubcategoryDialog}
      onClose={() => setShowSubcategoryDialog(false)}
      onConfirm={handleSubcategoryConfirm}
      inputLabel="Subcategory Name"
      placeholder="Enter subcategory name"
    />
    </div>
  );
};