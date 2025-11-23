"use client";

import { useState, FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import Sidebar, { NavigationContent } from "@/components/Sidebar";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  Bell, Search, Sun, Moon, Menu
} from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useTheme } from "@/hooks/use-theme";
import { apiClient } from "@/lib/api-client";

export default function OcrUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const { theme, toggleTheme } = useTheme();
  const [open, setOpen] = useState(false);

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
      const response = await apiClient.post("/api/ocr/upload", formData, {
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
    <div className="flex min-h-screen bg-background overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col transition-all duration-300 lg:ml-64">
        <header className="border-b bg-card px-4 py-3 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-3 flex-1">
            <Sheet open={open} onOpenChange={setOpen}><SheetTrigger asChild className="lg:hidden"><Button variant="outline" size="icon"><Menu className="h-5 w-5" /></Button></SheetTrigger><SheetContent side="left" className="p-0 w-64"><SheetHeader className="px-4 py-2 border-b dark:border-gray-800"><SheetTitle>Dashboard Navigation</SheetTitle></SheetHeader><NavigationContent setOpen={setOpen} /></SheetContent></Sheet>
            <div className="relative flex-1 max-w-full"><Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" /><Input placeholder="Search anything..." className="pl-10 w-full bg-background border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all duration-300" /></div>
          </div>
          <div className="flex items-center gap-[0px] sm:gap-[1px] md:gap-[2px] ml-[1px]">
            <Button variant="ghost" size="icon" className="relative hover:bg-blue-50 dark:hover:bg-gray-800 transition p-[5px]"><Bell className="h-4 w-4" /><span className="absolute -top-1 -right-1 h-3.5 w-3.5 bg-destructive rounded-full text-[9px] text-white flex items-center justify-center">3</span></Button>
            <Button variant="ghost" size="icon" onClick={toggleTheme} className="hover:bg-blue-50 dark:hover:bg-gray-800 transition p-[5px]">{theme === "dark" ? <Sun className="h-4 w-4 text-yellow-400" /> : <Moon className="h-4 w-4 text-blue-500" />}</Button>
            <Avatar className="cursor-pointer hover:scale-105 transition-transform duration-200 ml-[1px]"><AvatarFallback className="bg-primary text-primary-foreground text-[13px]">{typeof window !== 'undefined' ? localStorage.getItem("user_avatar")?.charAt(0).toUpperCase() || 'M' : 'M'}</AvatarFallback></Avatar>
          </div>
        </header>

        <main className="flex-1 p-4 md:p-6 overflow-y-auto">
          <div className="flex items-center justify-between space-y-2">
            <h2 className="text-3xl font-bold tracking-tight">Invoice OCR Upload</h2>
          </div>
          <Card className="w-full max-w-lg">
            <CardHeader>
              <CardTitle>Upload an Invoice Image</CardTitle>
              <CardDescription>
                Select an image file (e.g., PNG, JPG) of an invoice to automatically extract its data.
              </CardDescription>
            </CardHeader>
            <CardContent>
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
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
}