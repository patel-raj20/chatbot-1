/**
 * Admin RAG Hook
 * ==============
 * Custom hook for managing document uploads
 */

import { useState } from 'react';
import { uploadPDF } from '../lib/api';

export function useAdminRAG() {
  const [uploadStatus, setUploadStatus] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus("Uploading...");

    try {
      await uploadPDF(file);
      setUploadStatus(`✅ Document uploaded successfully!`);
      localStorage.setItem("rag_document_uploaded", "true");
      setTimeout(() => setUploadStatus(""), 5000);
    } catch (err) {
      setUploadStatus(`❌ Upload failed: ${err.message}`);
    } finally {
      setIsUploading(false);
      e.target.value = "";
    }
  };

  return {
    uploadStatus,
    isUploading,
    handleFileUpload
  };
}
