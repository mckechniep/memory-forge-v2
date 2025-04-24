import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export const CustomDialog = ({ 
  title, 
  isOpen, 
  onClose, 
  onConfirm, 
  inputLabel = "Name",
  placeholder = "",
  confirmText = "Confirm",
  cancelText = "Cancel"
}) => {
  const [value, setValue] = useState("");

  const handleConfirm = () => {
    onConfirm(value);
    setValue("");
  };

  const handleCancel = () => {
    onClose();
    setValue("");
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        <div className="py-4">
          <Label htmlFor="dialogInput">{inputLabel}</Label>
          <Input
            id="dialogInput"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder={placeholder}
            className="mt-2"
            autoFocus
          />
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={handleCancel}>
            {cancelText}
          </Button>
          <Button onClick={handleConfirm} disabled={!value.trim()}>
            {confirmText}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
