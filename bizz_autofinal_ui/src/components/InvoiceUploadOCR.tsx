"use client";

import { useState } from "react";
import axios from "axios";
import { Upload } from "lucide-react";

// NOTE: These are assumed imports from your project's UI library (e.g., shadcn/ui)
// If your component names are different, please adjust them.
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

// --- How to get company_id ---
// I am assuming you have an authentication context.
// If you don't, you'll need to fetch the company_id from wherever it's stored.
//
// Example using a hypothetical useAuth hook:
// import { useAuth } from "@/hooks/use-auth"; // Assuming you have this hook
//
// Inside the component:
// const { user } = useAuth();
// const companyId = user?.company_id;
//
// For this component, I will pass company_id as a prop for clarity.

interface InvoiceUploadOCRProps {
  companyId: string; // Expect companyId to be passed as a prop
  onUploadSuccess?: () => void; // Optional callback to refresh data
}

export default function InvoiceUploadOCR({ companyId, onUploadSuccess }: InvoiceUploadOCRProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      setFile(files[0]);
      setError(null); // Clear previous errors on new file selection
      setSuccess(null);
    }
  };

  const handleSubmit = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    if (!companyId) {
      setError("Could not determine company ID. Please ensure you are logged in.");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("company_id", companyId);
    
    // Use the environment variable for the API URL
    const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/invoice-processing/upload-invoice`;

    try {
      const response = await axios.post(apiUrl, formData, {
        headers: {
          // 'Content-Type': 'multipart/form-data' is automatically set by axios for FormData
        },
      });

      if (response.data.success) {
        setSuccess(`Successfully processed invoice! (ID: ${response.data.invoice_id})`);
        setFile(null); // Clear the file input
        if (onUploadSuccess) {
          onUploadSuccess(); // Call the callback to refresh the invoice list
        }
      } else {
        setError(response.data.message || "An unknown error occurred.");
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || "An unexpected error occurred during upload.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded-lg bg-card text-card-foreground shadow-sm w-full max-w-md mx-auto">
      <h3 className="text-lg font-semibold mb-2">Process New Invoice</h3>
      <p className="text-sm text-muted-foreground mb-4">
        Upload an invoice (PDF, PNG, JPG) to automatically extract its details and update your inventory.
      </p>
      <div className="flex items-center space-x-2 mb-4">
        <Input
          type="file"
          onChange={handleFileChange}
          accept=".pdf,.png,.jpg,.jpeg"
          className="flex-grow"
          disabled={loading}
        />
      </div>
      <Button
        onClick={handleSubmit}
        disabled={!file || loading}
        className="w-full"
      >
        <Upload className="w-4 h-4 mr-2" />
        {loading ? "Processing..." : "Upload & Process"}
      </Button>
      {error && <p className="mt-2 text-sm text-destructive">{error}</p>}
      {success && <p className="mt-2 text-sm text-green-600">{success}</p>}
    </div>
  );
}
