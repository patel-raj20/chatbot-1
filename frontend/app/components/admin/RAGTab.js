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
    <div className="flex-1 overflow-y-auto p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Upload Section */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-4">📄 Upload Document for RAG</h2>
          <p className="text-purple-200 mb-6">
            Upload a PDF document to enable AI-powered question answering based on the document content.
          </p>

          <div className="bg-white/5 rounded-xl p-6 border-2 border-dashed border-purple-400 hover:border-purple-300 transition-colors">
            <label className="flex flex-col items-center cursor-pointer">
              <div className="w-16 h-16 bg-gradient-to-br from-violet-500 to-purple-600 rounded-full flex items-center justify-center mb-4">
                <span className="text-3xl">📤</span>
              </div>
              <span className="text-lg font-semibold text-white mb-2">
                {isUploading ? "Uploading..." : "Click to upload PDF"}
              </span>
              <span className="text-sm text-purple-300 mb-4">
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
                <div className="px-6 py-3 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-xl transition-all">
                  Choose File
                </div>
              )}
              {isUploading && (
                <div className="px-6 py-3 bg-gray-500 text-white rounded-lg font-semibold">
                  Processing...
                </div>
              )}
            </label>
          </div>

          {uploadStatus && (
            <div className={`mt-6 p-4 rounded-lg ${
              uploadStatus.includes("✅") 
                ? "bg-green-500/20 border border-green-500/50 text-green-200" 
                : "bg-red-500/20 border border-red-500/50 text-red-200"
            }`}>
              {uploadStatus}
            </div>
          )}
        </div>

        {/* Uploaded Documents List */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-4">📚 Uploaded Documents</h2>
          
          {loadingDocs ? (
            <p className="text-purple-200">Loading documents...</p>
          ) : documents.length === 0 ? (
            <p className="text-purple-200">No documents uploaded yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left border-b border-white/20">
                    <th className="pb-3 text-purple-300 font-semibold">Filename</th>
                    <th className="pb-3 text-purple-300 font-semibold">Upload Date</th>
                    <th className="pb-3 text-purple-300 font-semibold">Chunks</th>
                    <th className="pb-3 text-purple-300 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.id} className="border-b border-white/10 hover:bg-white/5">
                      <td className="py-4 text-white">{doc.filename}</td>
                      <td className="py-4 text-purple-200">
                        {new Date(doc.upload_date).toLocaleString()}
                      </td>
                      <td className="py-4 text-purple-200">{doc.chunk_count}</td>
                      <td className="py-4 space-x-2">
                        <button
                          onClick={() => handleDownload(doc.id)}
                          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors"
                          title="Download PDF"
                        >
                          ⬇️ Download
                        </button>
                        <button
                          onClick={() => setDeleteConfirm(doc)}
                          className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm transition-colors"
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
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
          <h3 className="text-lg font-semibold text-white mb-3">How it works:</h3>
          <ul className="space-y-2 text-purple-200 text-sm">
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
          <div className="bg-gradient-to-br from-purple-900 to-indigo-900 p-8 rounded-2xl shadow-2xl max-w-md w-full mx-4 border border-white/20">
            <h3 className="text-2xl font-bold text-white mb-4">⚠️ Confirm Deletion</h3>
            <p className="text-purple-200 mb-2">
              Are you sure you want to delete:
            </p>
            <p className="text-white font-semibold mb-4">
              {deleteConfirm.filename}
            </p>
            <p className="text-sm text-red-300 mb-6">
              This will permanently remove the PDF from storage and delete all {deleteConfirm.chunk_count} chunks from the vector database. This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="flex-1 px-4 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-semibold transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteConfirm.id)}
                className="flex-1 px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition-colors"
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
