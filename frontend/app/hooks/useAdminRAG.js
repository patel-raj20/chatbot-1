/**
 * Admin RAG Hook
 * ==============
 * Custom hook for managing document uploads, listing, and deletion
 */

import { useState, useEffect } from 'react';
import { uploadPDF, listDocuments, deleteDocument, downloadDocument } from '../lib/api';

export function useAdminRAG() {
  const [uploadStatus, setUploadStatus] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoadingDocs(true);
    try {
      const docs = await listDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setLoadingDocs(false);
    }
  };

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
      // Refresh document list
      await loadDocuments();
    } catch (err) {
      setUploadStatus(`❌ Upload failed: ${err.message}`);
    } finally {
      setIsUploading(false);
      e.target.value = "";
    }
  };

  const handleDelete = async (docId) => {
    try {
      await deleteDocument(docId);
      setDeleteConfirm(null);
      // Refresh document list
      await loadDocuments();
    } catch (err) {
      alert(`Failed to delete document: ${err.message}`);
    }
  };

  const handleDownload = async (docId) => {
    try {
      await downloadDocument(docId);
    } catch (err) {
      alert(`Failed to download document: ${err.message}`);
    }
  };

  return {
    uploadStatus,
    isUploading,
    handleFileUpload,
    documents,
    loadingDocs,
    deleteConfirm,
    setDeleteConfirm,
    handleDelete,
    handleDownload
  };
}
