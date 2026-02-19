/**
 * RAG Tab Component
 * =================
 * Document upload and management interface
 */

export default function RAGTab({ 
  uploadStatus, 
  isUploading, 
  handleFileUpload,
  documents,
  loadingDocs,
  deleteConfirm,
  setDeleteConfirm,
  handleDelete,
  handleDownload
}) {
  return (
    <div className="flex-1 overflow-y-auto p-8 bg-[#F5F7FA]">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Upload Section */}
        <div className="bg-white rounded-xl p-8 border border-[#E5E7EB] shadow-md">
          <h2 className="text-2xl font-bold text-[#1F2937] mb-4">📄 Upload Document for RAG</h2>
          <p className="text-[#6B7280] mb-6">
            Upload a PDF document to enable AI-powered question answering based on the document content.
          </p>

          <div className="bg-[#F5F7FA] rounded-xl p-6 border-2 border-dashed border-[#E5E7EB] hover:border-[#4F6BED] transition-all duration-200">
            <label className="flex flex-col items-center cursor-pointer">
              <div className="w-16 h-16 bg-[#4F6BED] rounded-full flex items-center justify-center mb-4">
                <span className="text-3xl">📤</span>
              </div>
              <span className="text-lg font-semibold text-[#1F2937] mb-2">
                {isUploading ? "Uploading..." : "Click to upload PDF"}
              </span>
              <span className="text-sm text-[#6B7280] mb-4">
                PDF files only
              </span>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                disabled={isUploading}
                className="hidden"
              />
              {!isUploading && (
                <div className="px-6 py-3 bg-[#4F6BED] hover:bg-[#3D56D9] text-white rounded-xl font-semibold transition-all duration-200 shadow-md">
                  Choose File
                </div>
              )}
              {isUploading && (
                <div className="px-6 py-3 bg-[#9CA3AF] text-white rounded-xl font-semibold">
                  Processing...
                </div>
              )}
            </label>
          </div>

          {uploadStatus && (
            <div className={`mt-6 p-4 rounded-xl ${
              uploadStatus.includes("✅") 
                ? "bg-[#E6F7F5] border border-[#2CB1A6] text-[#0F3D3A]" 
                : "bg-red-50 border border-[#E5533D] text-[#E5533D]"
            }`}>
              {uploadStatus}
            </div>
          )}
        </div>

        {/* Uploaded Documents List */}
        <div className="bg-white rounded-xl p-8 border border-[#E5E7EB] shadow-md">
          <h2 className="text-2xl font-bold text-[#1F2937] mb-4">📚 Uploaded Documents</h2>
          
          {loadingDocs ? (
            <p className="text-[#6B7280]">Loading documents...</p>
          ) : documents.length === 0 ? (
            <p className="text-[#6B7280]">No documents uploaded yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left border-b border-[#E5E7EB]">
                    <th className="pb-3 text-[#6B7280] font-semibold">Filename</th>
                    <th className="pb-3 text-[#6B7280] font-semibold">Upload Date</th>
                    <th className="pb-3 text-[#6B7280] font-semibold">Chunks</th>
                    <th className="pb-3 text-[#6B7280] font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.id} className="border-b border-[#E5E7EB] hover:bg-[#F5F7FA]">
                      <td className="py-4 text-[#1F2937]">{doc.filename}</td>
                      <td className="py-4 text-[#6B7280]">
                        {new Date(doc.upload_date).toLocaleString()}
                      </td>
                      <td className="py-4 text-[#6B7280]">{doc.chunk_count}</td>
                      <td className="py-4 space-x-2">
                        <button
                          onClick={() => handleDownload(doc.id)}
                          className="px-3 py-1 bg-[#4F6BED] hover:bg-[#3D56D9] text-white rounded-lg text-sm transition-all duration-200"
                          title="Download PDF"
                        >
                          ⬇️ Download
                        </button>
                        <button
                          onClick={() => setDeleteConfirm(doc)}
                          className="px-3 py-1 bg-[#E5533D] hover:bg-[#CC3F2B] text-white rounded-lg text-sm transition-all duration-200"
                          title="Delete document"
                        >
                          🗑️ Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* How it works section */}
        <div className="bg-white rounded-xl p-8 border border-[#E5E7EB] shadow-md">
          <h3 className="text-lg font-semibold text-[#1F2937] mb-3">How it works:</h3>
          <ul className="space-y-2 text-[#6B7280] text-sm">
            <li className="flex items-start gap-2">
              <span>1️⃣</span>
              <span>Upload a PDF document using the button above</span>
            </li>
            <li className="flex items-start gap-2">
              <span>2️⃣</span>
              <span>The document will be processed and indexed for AI search</span>
            </li>
            <li className="flex items-start gap-2">
              <span>3️⃣</span>
              <span>In the chatbot, users can ask questions about the document</span>
            </li>
            <li className="flex items-start gap-2">
              <span>4️⃣</span>
              <span>The AI will answer based on document content first, then fall back to normal chat</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white p-8 rounded-xl shadow-2xl max-w-md w-full mx-4 border border-[#E5E7EB]">
            <h3 className="text-2xl font-bold text-[#1F2937] mb-4">⚠️ Confirm Deletion</h3>
            <p className="text-[#6B7280] mb-2">
              Are you sure you want to delete:
            </p>
            <p className="text-[#1F2937] font-semibold mb-4">
              {deleteConfirm.filename}
            </p>
            <p className="text-sm text-[#E5533D] mb-6">
              This will permanently remove the PDF from storage and delete all {deleteConfirm.chunk_count} chunks from the vector database. This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="flex-1 px-4 py-3 bg-[#6B7280] hover:bg-[#4B5563] text-white rounded-xl font-semibold transition-all duration-200 shadow-md"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteConfirm.id)}
                className="flex-1 px-4 py-3 bg-[#E5533D] hover:bg-[#CC3F2B] text-white rounded-xl font-semibold transition-all duration-200 shadow-md"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
