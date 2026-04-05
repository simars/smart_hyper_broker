"use client";

import { useState, useRef } from "react";
import { UploadCloud, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export function UploadRbcCsv() {
  const [isUploading, setIsUploading] = useState(false);
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setStatus("idle");
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/api/upload/rbc", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (res.ok && data.status === "success") {
        setStatus("success");
        setMessage("RBC holdings updated.");
        // Hide success message after 3s
        setTimeout(() => setStatus("idle"), 3000);
      } else {
        setStatus("error");
        setMessage(data.message || "Upload failed.");
      }
    } catch (err) {
      setStatus("error");
      setMessage("Network error during upload.");
    } finally {
      setIsUploading(false);
      // Reset input so same file can be uploaded again if needed
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div className="flex items-center gap-2">
      <input
        type="file"
        accept=".csv"
        className="hidden"
        ref={fileInputRef}
        onChange={handleFileChange}
      />
      
      {status === "idle" && (
        <Button 
          variant="outline" 
          size="sm" 
          className="h-8 text-xs bg-zinc-100 dark:bg-zinc-800 border-none hover:bg-zinc-200 dark:hover:bg-zinc-700"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
        >
          {isUploading ? (
            <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin text-zinc-500" />
          ) : (
            <UploadCloud className="w-3.5 h-3.5 mr-1.5 text-zinc-500 text-indigo-500" />
          )}
          Import RBC
        </Button>
      )}

      {status === "success" && (
        <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 px-3 py-1.5 rounded-lg">
          <CheckCircle2 className="w-3.5 h-3.5" />
          {message}
        </span>
      )}

      {status === "error" && (
        <span className="flex items-center gap-1.5 text-xs font-medium text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-500/10 px-3 py-1.5 rounded-lg" title={message}>
          <AlertCircle className="w-3.5 h-3.5" />
          Failed
        </span>
      )}
    </div>
  );
}
