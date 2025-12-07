"use client";

import { useState, FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-config";

interface OcrUploadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onUploadSuccess: () => void;
}

export default function OcrUploadDialog({ open, onOpenChange, onUploadSuccess }: OcrUploadDialogProps) {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
      setStatus("idle");
      setMessage("");
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) {
      setMessage("Please select a file first.");
      setStatus("error");
      return;
    }

    setStatus("uploading");
    setMessage("Uploading file...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await apiClient.post(API_ENDPOINTS.invoiceUpload, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const data = response.data;

      setStatus("success");
      setMessage(`File '${data.filename}' uploaded and queued for processing.`);
      const fileInput = document.getElementById('invoice-file') as HTMLInputElement;
      if(fileInput) fileInput.value = "";
      setFile(null);
      onUploadSuccess();
      setTimeout(() => {
        onOpenChange(false);
      }, 2000);

    } catch (error: any) {
      setStatus("error");
      if (error.response) {
        setMessage(`Upload failed: ${error.response.data.detail || "Server error"}`);
      } else if (error.request) {
        setMessage("Upload failed: No response from server.");
      } else {
        setMessage(`Upload failed: ${error.message}`);
      }
      console.error("Upload error:", error);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upload an Invoice Image</DialogTitle>
          <DialogDescription>
            Select an image file (e.g., PNG, JPG) of an invoice to automatically extract its data.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="invoice-file">Invoice File</Label>
            <Input id="invoice-file" type="file" onChange={handleFileChange} accept="image/*" />
          </div>
          <Button type="submit" disabled={status === "uploading" || !file}>
            {status === "uploading" ? "Uploading..." : "Upload and Process"}
          </Button>
        </form>
        {message && (
          <div
            className={`mt-4 text-sm font-medium ${
              status === "error" ? "text-red-600" : "text-green-600"
            }`}
          >
            {message}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
