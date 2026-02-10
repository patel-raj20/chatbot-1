/**
 * RAG Tab Component
 * =================
 * Document upload interface
 */

export default function RAGTab({ uploadStatus, isUploading, handleFileUpload }) {
  return (
    <div className="flex-1 overflow-y-auto p-8">
      <div className="max-w-2xl mx-auto">
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

          <div className="mt-8 bg-white/5 rounded-xl p-6">
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
      </div>
    </div>
  );
}
