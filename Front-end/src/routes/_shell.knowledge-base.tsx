import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect, useRef } from "react";
import { Database, UploadCloud, FileText, Trash2, AlertCircle, CheckCircle } from "lucide-react";
import { Button } from "@/components/agentforge/primitives";

export const Route = createFileRoute("/_shell/knowledge-base")({
  head: () => ({
    meta: [{ title: "Knowledge Base — AgentForge" }],
  }),
  component: KnowledgeBasePage,
});

interface KnowledgeFile {
  name: string;
  size: number;
  uploadedAt: string;
}

function formatBytes(bytes: number, decimals = 2) {
  if (!bytes) return "0 Bytes";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

function KnowledgeBasePage() {
  const [filesList, setFilesList] = useState<KnowledgeFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchFiles = () => {
    fetch("/api/knowledge")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setFilesList(data);
        }
      })
      .catch((err) => console.error("Error fetching knowledge files", err));
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      setSelectedFiles(Array.from(e.dataTransfer.files));
    }
  };

  const uploadFiles = async () => {
    if (selectedFiles.length === 0) {
      setErrorMsg("Please select at least one document to upload.");
      return;
    }

    setUploading(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      for (const file of selectedFiles) {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("/api/knowledge/upload", {
          method: "POST",
          body: formData,
        });

        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(errorData.detail || `Failed to upload "${file.name}"`);
        }
      }

      setSuccessMsg(`Successfully ingested ${selectedFiles.length} file(s) into RAG.`);
      setSelectedFiles([]);
      if (fileInputRef.current) fileInputRef.current.value = "";
      fetchFiles();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to upload one or more files.");
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteFile = (fileName: string) => {
    if (!confirm(`Are you sure you want to delete "${fileName}"?`)) return;

    fetch(`/api/knowledge/${fileName}`, {
      method: "DELETE",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to delete document");
        setSuccessMsg(`Document "${fileName}" deleted successfully.`);
        fetchFiles();
        setTimeout(() => setSuccessMsg(""), 3000);
      })
      .catch((err) => console.error("Error deleting file:", err));
  };

  return (
    <div className="p-8 max-w-[1200px] mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
          <Database size={28} className="text-accent" /> Knowledge Base
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Upload company files (PDF, DOCX, TXT, CSV) to the RAG database to power knowledge-aware agents.
        </p>
      </div>

      {successMsg && (
        <div className="rounded-lg border border-success/20 bg-success-tint px-4 py-3 text-sm text-success flex items-center gap-2 af-fade-in">
          <CheckCircle size={16} /> {successMsg}
        </div>
      )}

      {errorMsg && (
        <div className="rounded-lg border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive flex items-center gap-2 af-fade-in">
          <AlertCircle size={16} /> {errorMsg}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-[1.2fr_1.8fr] gap-6">
        {/* Upload Container */}
        <div className="rounded-xl border border-border bg-surface p-6 space-y-4 flex flex-col justify-between h-[360px]">
          <div>
            <h2 className="text-[15px] font-semibold text-foreground">Ingest Documents</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Files are parsed, chunked, and stored locally in Chroma vector storage.
            </p>
          </div>

          <div
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className="flex-1 border border-dashed border-border rounded-lg flex flex-col items-center justify-center p-4 cursor-pointer hover:border-accent/50 hover:bg-surface-muted/30 transition-all my-2"
          >
            <UploadCloud size={32} className="text-muted-foreground mb-2" />
            <span className="text-xs font-semibold text-foreground text-center">
              Drag & drop documents here or click to browse
            </span>
            <span className="text-[10px] text-muted-foreground text-center mt-1">
              Supports PDF, DOCX, TXT, CSV (max 10MB)
            </span>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              multiple
              accept=".pdf,.docx,.txt,.csv"
              className="hidden"
            />
          </div>

          {selectedFiles.length > 0 && (
            <div className="text-xs text-foreground bg-surface-muted border border-border rounded px-3 py-1.5 line-clamp-1">
              Selected: {selectedFiles.map((f) => f.name).join(", ")}
            </div>
          )}

          {uploading ? (
            <div className="space-y-2">
              <div className="h-1.5 w-full bg-border rounded-full overflow-hidden">
                <div className="h-full bg-accent af-progress rounded-full" />
              </div>
              <p className="text-[11px] text-muted-foreground text-center">Injesting text chunks into Chroma vector store...</p>
            </div>
          ) : (
            <Button onClick={uploadFiles} className="w-full">
              ✨ Ingest Documents
            </Button>
          )}
        </div>

        {/* Files List Container */}
        <div className="rounded-xl border border-border bg-surface p-6 flex flex-col h-[360px]">
          <div className="mb-4">
            <h2 className="text-[15px] font-semibold text-foreground">Ingested Context Library</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Available documents active in custom agent queries.
            </p>
          </div>

          <div className="flex-1 overflow-y-auto af-scroll pr-1 divide-y divide-border">
            {filesList.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-4">
                <FileText size={28} className="text-muted-foreground/45 mb-2" />
                <p className="text-xs text-muted-foreground">No documents ingested in RAG vector storage yet.</p>
              </div>
            ) : (
              filesList.map((file) => (
                <div key={file.name} className="flex items-center justify-between py-2.5 first:pt-0 last:pb-0">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <FileText size={18} className="text-accent shrink-0" />
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-foreground truncate" title={file.name}>
                        {file.name}
                      </p>
                      <p className="text-[10px] text-muted-foreground mt-0.5">
                        {formatBytes(file.size)} | Ingested on {file.uploadedAt}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteFile(file.name)}
                    className="h-8 w-8 rounded-lg flex items-center justify-center text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors shrink-0"
                    aria-label="Delete"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
