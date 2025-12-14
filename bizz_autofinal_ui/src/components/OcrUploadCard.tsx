"use client";

import { useState, FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { apiClient } from "@/lib/api-client";
import { X } from "lucide-react";

interface OcrUploadCardProps {
  companyId: string; // The user's company ID is required for the upload
  onClose: () => void;
  onUploadSuccess?: () => void; // Optional: To refresh data after success
}

export default function OcrUploadCard({ companyId, onClose, onUploadSuccess }: OcrUploadCardProps) {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
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
    
    if (!companyId) {
      setMessage("Company ID is missing. Cannot upload.");
      setStatus("error");
      return;
    }

    setStatus("uploading");
    setMessage("Processing document...");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("company_id", companyId);

    // --- ✅ Debugging Logs ---
    console.log('Sending company_id:', companyId);
    console.log('FormData contents:', Array.from(formData.entries()));
    // -------------------------

    try {
      // ✅ Corrected the API endpoint
      const response = await apiClient.post("/api/invoice-processing/upload-invoice", formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const data = response.data;
      
      if (data.success) {
        setStatus("success");
        setMessage(`Success! Invoice processed (ID: ${data.invoice_id}). Items processed: ${data.items_processed}.`);
        setFile(null);
        // Optionally call the success callback to refresh the parent component's data
        if (onUploadSuccess) {
            onUploadSuccess();
        }
      } else {
        setStatus("error");
        setMessage(data.message || "An unknown error occurred during processing.");
      }

    } catch (error: any) {
      setStatus("error");
      const errorMessage = error.response?.data?.detail || error.message || "An unexpected network error occurred.";
      setMessage(`Upload failed: ${errorMessage}`);
      console.error("Upload error:", error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Upload and Process Document</CardTitle>
            <X className="cursor-pointer" onClick={onClose} />
          </div>
          <CardDescription>
            Upload a PDF or image file of an invoice or inventory list. The system will automatically extract the items and update your inventory.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid w-full max-w-sm items-center gap-1.5">
              <Label htmlFor="invoice-file">Document File</Label>
              <Input 
                id="invoice-file" 
                type="file" 
                onChange={handleFileChange} 
                accept=".pdf,.png,.jpg,.jpeg" 
              />
            </div>
            <Button type="submit" disabled={status === "uploading" || !file}>
              {status === "uploading" ? "Processing..." : "Upload and Process"}
            </Button>
          </form>
          {message && (
            <div
              className={`mt-4 text-sm font-medium ${
                status === "error" ? "text-red-500" : "text-green-600"
              }`}
            >
              {message}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
