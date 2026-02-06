/**
 * Admin Panel
 * ===========
 * Comprehensive admin interface for managing the chatbot.
 * 
 * AUTHENTICATION: Requires admin role (role='admin')
 * AUTHORIZATION: Only admins can access this panel
 * 
 * FEATURES:
 *   - Flow Editor: Visual conversation tree builder with drag-and-drop
 *   - FAQ Management: Create/edit/delete frequently asked questions
 *   - Chat History: View user conversations by session
 *   - Document Upload: Upload PDFs for RAG knowledge base
 * 
 * TABS:
 *   1. Flow: ReactFlow-based conversation tree editor
 *   2. FAQs: FAQ CRUD interface
 *   3. Chat History: Session browser with message viewer
 *   4. Document Upload: RAG document management
 */

"use client";

import { useEffect, useState, useCallback } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  MarkerType,
  Handle,
  Position,
} from "reactflow";
import "reactflow/dist/style.css";
import { uploadPDF } from "../lib/api";
import ProtectedRoute from "../components/ProtectedRoute";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Custom Node Component
function CustomNode({ data }) {
  return (
    <div className="px-4 py-3 rounded-lg bg-white border-2 border-purple-500 shadow-lg min-w-[200px] max-w-[300px]">
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 !bg-purple-500"
      />
      
      {data.is_entry && (
        <div className="mb-2">
          <span className="px-2 py-1 bg-green-500 text-white text-xs font-semibold rounded-full">
            ENTRY
          </span>
        </div>
      )}
      {data.trigger_text && (
        <div className="text-xs text-purple-600 mb-1 font-mono bg-purple-50 px-2 py-1 rounded">
          Trigger: {data.trigger_text}
        </div>
      )}
      <div className="text-sm text-gray-800 font-medium break-words">{data.message_text}</div>
      <div className="mt-2 flex gap-1 flex-wrap">
        <button
          onClick={(e) => {
            e.stopPropagation();
            data.onEdit();
          }}
          className="px-2 py-1 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded transition-colors"
        >
          Edit
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            data.onDelete();
          }}
          className="px-2 py-1 bg-red-500 hover:bg-red-600 text-white text-xs rounded transition-colors"
        >
          Delete
        </button>
      </div>
      <div className="mt-2 text-xs text-gray-500 italic">
        💡 Drag from right edge →
      </div>
      
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 !bg-purple-500"
      />
    </div>
  );
}

const nodeTypes = {
  custom: CustomNode,
};

// ============= MAIN ADMIN PANEL COMPONENT =============

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
};

function AdminPanel() {
  const [activeTab, setActiveTab] = useState("flow");
  
  // Flow Editor State
  const [backendNodes, setBackendNodes] = useState([]);
  const [backendEdges, setBackendEdges] = useState([]);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showNodeForm, setShowNodeForm] = useState(false);
  
  const [nodeForm, setNodeForm] = useState({
    message_text: "",
    trigger_text: "",
    is_entry: false,
    position_x: 250,
    position_y: 100
  });

  // FAQ State
  const [faqs, setFaqs] = useState([]);
  const [showFaqForm, setShowFaqForm] = useState(false);
  const [editingFaq, setEditingFaq] = useState(null);
  const [faqForm, setFaqForm] = useState({
    question: "",
    answer: "",
    order: "0",
    is_active: true
  });

  // RAG State
  const [uploadStatus, setUploadStatus] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  // Chat History State
  const [sessions, setSessions] = useState([]);
  const [expandedSessions, setExpandedSessions] = useState({}); // session_id -> boolean
  const [messagesBySession, setMessagesBySession] = useState({}); // session_id -> messages array

  useEffect(() => {
    if (activeTab === "flow") {
      fetchNodes();
    } else if (activeTab === "faq") {
      fetchFaqs();
    } else if (activeTab === "history") {
      fetchSessions();
    }
  }, [activeTab]);

  // Flow Functions
  const fetchNodes = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/nodes`, {
        headers: getAuthHeaders()
      });
      const data = await res.json();
      setBackendNodes(data);
      convertToFlowNodes(data);
    } catch (err) {
      console.error("Failed to fetch nodes:", err);
    }
  };

  const convertToFlowNodes = (backendData) => {
    const flowNodes = backendData.map((node, index) => ({
      id: node.id,
      type: "custom",
      position: { 
        x: node.position_x || (index % 3) * 350, 
        y: node.position_y || Math.floor(index / 3) * 200 
      },
      data: {
        message_text: node.message_text,
        trigger_text: node.trigger_text,
        is_entry: node.is_entry,
        onEdit: () => startEdit(node),
        onDelete: () => deleteNode(node.id),
      },
      sourcePosition: 'right',
      targetPosition: 'left',
    }));

    const flowEdges = [];
    backendData.forEach((node) => {
      node.outgoing_edges.forEach((edge) => {
        flowEdges.push({
          id: edge.id,
          source: node.id,
          target: edge.to_node_id,
          label: edge.option_text || "auto",
          type: "smoothstep",
          animated: !edge.option_text,
          markerEnd: {
            type: MarkerType.ArrowClosed,
            width: 20,
            height: 20,
            color: "#9333ea",
          },
          style: {
            stroke: "#9333ea",
            strokeWidth: 2,
          },
        });
      });
    });

    setNodes(flowNodes);
    setEdges(flowEdges);
    
    const allEdges = [];
    backendData.forEach(node => {
      allEdges.push(...node.outgoing_edges);
    });
    setBackendEdges(allEdges);
  };

  const onConnect = useCallback(
    async (params) => {
      const optionText = prompt("Enter option text for this connection (or leave empty for auto-transition):");
      if (optionText === null) return;
      
      try {
        await fetch(`${API_BASE_URL}/admin/edges`, {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            from_node_id: params.source,
            to_node_id: params.target,
            option_text: optionText || null
          })
        });
        fetchNodes();
      } catch (err) {
        console.error("Failed to create edge:", err);
      }
    },
    []
  );

  const onNodeDragStop = useCallback(
    async (event, node) => {
      try {
        await fetch(`${API_BASE_URL}/admin/nodes/${node.id}`, {
          method: "PUT",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            position_x: node.position.x,
            position_y: node.position.y,
          }),
        });
      } catch (err) {
        console.error("Failed to update node position:", err);
      }
    },
    []
  );

  const createNode = async () => {
    try {
      await fetch(`${API_BASE_URL}/admin/nodes`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(nodeForm)
      });
      setNodeForm({ message_text: "", trigger_text: "", is_entry: false, position_x: 250, position_y: 100 });
      setShowNodeForm(false);
      fetchNodes();
    } catch (err) {
      console.error("Failed to create node:", err);
    }
  };

  const updateNode = async (nodeId) => {
    try {
      await fetch(`${API_BASE_URL}/admin/nodes/${nodeId}`, {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify(nodeForm)
      });
      setNodeForm({ message_text: "", trigger_text: "", is_entry: false, position_x: 250, position_y: 100 });
      setSelectedNode(null);
      fetchNodes();
    } catch (err) {
      console.error("Failed to update node:", err);
    }
  };

  const deleteNode = async (nodeId) => {
    if (!confirm("Delete this node and all its connections?")) return;
    
    try {
      await fetch(`${API_BASE_URL}/admin/nodes/${nodeId}`, {
        method: "DELETE"
      });
      fetchNodes();
    } catch (err) {
      console.error("Failed to delete node:", err);
    }
  };

  const deleteEdge = async (edgeId) => {
    if (!confirm("Delete this connection?")) return;
    
    try {
      await fetch(`${API_BASE_URL}/admin/edges/${edgeId}`, {
        method: "DELETE"
      });
      fetchNodes();
    } catch (err) {
      console.error("Failed to delete edge:", err);
    }
  };

  const startEdit = (node) => {
    setSelectedNode(node.id);
    setNodeForm({
      message_text: node.message_text,
      trigger_text: node.trigger_text || "",
      is_entry: node.is_entry,
      position_x: node.position_x || 250,
      position_y: node.position_y || 100
    });
  };

  // FAQ Functions
  const fetchFaqs = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/faqs`);
      const data = await res.json();
      setFaqs(data);
    } catch (err) {
      console.error("Failed to fetch FAQs:", err);
    }
  };

  const createFaq = async () => {
    try {
      await fetch(`${API_BASE_URL}/admin/faqs`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(faqForm)
      });
      setFaqForm({ question: "", answer: "", order: "0", is_active: true });
      setShowFaqForm(false);
      fetchFaqs();
    } catch (err) {
      console.error("Failed to create FAQ:", err);
    }
  };

  const updateFaq = async (faqId) => {
    try {
      await fetch(`${API_BASE_URL}/admin/faqs/${faqId}`, {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify(faqForm)
      });
      setFaqForm({ question: "", answer: "", order: "0", is_active: true });
      setEditingFaq(null);
      fetchFaqs();
    } catch (err) {
      console.error("Failed to update FAQ:", err);
    }
  };

  const deleteFaq = async (faqId) => {
    if (!confirm("Delete this FAQ?")) return;
    
    try {
      await fetch(`${API_BASE_URL}/admin/faqs/${faqId}`, {
        method: "DELETE"
      });
      fetchFaqs();
    } catch (err) {
      console.error("Failed to delete FAQ:", err);
    }
  };

  const startEditFaq = (faq) => {
    setEditingFaq(faq.id);
    setFaqForm({
      question: faq.question,
      answer: faq.answer,
      order: faq.order,
      is_active: faq.is_active
    });
    setShowFaqForm(true);
  };
  
  // Chat History Functions
  const fetchSessions = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/chat/sessions`);
      const data = await res.json();
      setSessions(data);
    } catch (err) {
      console.error("Failed to fetch sessions:", err);
    }
  };

  const fetchSessionMessages = async (sessionId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/chat/sessions/${sessionId}`);
      const data = await res.json();
      setMessagesBySession(prev => ({ ...prev, [sessionId]: data }));
    } catch (err) {
      console.error("Failed to fetch session messages:", err);
    }
  };

  const toggleSession = async (sessionId) => {
    setExpandedSessions(prev => ({ ...prev, [sessionId]: !prev[sessionId] }));
    const willExpand = !expandedSessions[sessionId];
    if (willExpand && !messagesBySession[sessionId]) {
      await fetchSessionMessages(sessionId);
    }
  };
  // RAG Functions
  /**
   * Upload PDF document to RAG system
   * 
   * @param {Event} e - File input change event
   */
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
  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header with Tabs */}
      <div className="bg-slate-900/50 backdrop-blur-lg border-b border-white/10 p-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-white">Admin Panel</h1>
          <a href="/" className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors text-sm">
            ← Back to Chat
          </a>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab("history")}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === "history"
                ? "bg-purple-600 text-white shadow-lg"
                : "bg-white/10 text-purple-200 hover:bg-white/20"
            }`}
          >
            🕘 Chat History
          </button>
          <button
            onClick={() => setActiveTab("flow")}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === "flow"
                ? "bg-purple-600 text-white shadow-lg"
                : "bg-white/10 text-purple-200 hover:bg-white/20"
            }`}
          >
            🔀 Flow Builder
          </button>
          <button
            onClick={() => setActiveTab("faq")}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === "faq"
                ? "bg-purple-600 text-white shadow-lg"
                : "bg-white/10 text-purple-200 hover:bg-white/20"
            }`}
          >
            ❓ FAQ Management
          </button>
          <button
            onClick={() => setActiveTab("rag")}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === "rag"
                ? "bg-purple-600 text-white shadow-lg"
                : "bg-white/10 text-purple-200 hover:bg-white/20"
            }`}
          >
            📄 Document Upload
          </button>
        </div>
      </div>

      {/* Flow Builder Tab */}
      {activeTab === "flow" && (
        <div className="flex flex-1 overflow-hidden">
          <div className="w-96 bg-slate-900/50 backdrop-blur-lg border-r border-white/10 overflow-y-auto">
            <div className="p-6">
              <button
                onClick={() => {
                  setShowNodeForm(true);
                  setSelectedNode(null);
                  setNodeForm({ message_text: "", trigger_text: "", is_entry: false, position_x: 250, position_y: 100 });
                }}
                className="w-full px-6 py-3 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
              >
                + Add New Node
              </button>

              {(showNodeForm || selectedNode) && (
                <div className="mt-6 bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20">
                  <h3 className="text-lg font-bold text-white mb-4">
                    {selectedNode ? "Edit Node" : "Create New Node"}
                  </h3>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-purple-200 mb-1 text-sm">Message Text *</label>
                      <textarea
                        value={nodeForm.message_text}
                        onChange={(e) => setNodeForm({...nodeForm, message_text: e.target.value})}
                        className="w-full px-3 py-2 bg-white/5 border border-purple-300/30 rounded-lg text-white text-sm"
                        rows="3"
                      />
                    </div>
                    <div>
                      <label className="block text-purple-200 mb-1 text-sm">Trigger Text</label>
                      <input
                        type="text"
                        value={nodeForm.trigger_text}
                        onChange={(e) => setNodeForm({...nodeForm, trigger_text: e.target.value})}
                        className="w-full px-3 py-2 bg-white/5 border border-purple-300/30 rounded-lg text-white text-sm"
                      />
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={nodeForm.is_entry}
                        onChange={(e) => setNodeForm({...nodeForm, is_entry: e.target.checked})}
                        className="w-4 h-4"
                      />
                      <label className="text-purple-200 text-sm">Is Entry Node</label>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => selectedNode ? updateNode(selectedNode) : createNode()}
                        className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition-colors text-sm"
                      >
                        {selectedNode ? "Update" : "Create"}
                      </button>
                      <button
                        onClick={() => {
                          setShowNodeForm(false);
                          setSelectedNode(null);
                        }}
                        className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-semibold transition-colors text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}

              <div className="mt-6 bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20">
                <h3 className="text-lg font-bold text-white mb-4">Connections ({backendEdges.length})</h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {backendNodes.map(node => (
                    node.outgoing_edges.map(edge => (
                      <div key={edge.id} className="bg-purple-900/30 px-3 py-2 rounded-lg">
                        <div className="text-xs text-purple-100 mb-1">
                          {node.message_text.substring(0, 30)}... →
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-purple-300">{edge.option_text || "(auto)"}</span>
                          <button onClick={() => deleteEdge(edge.id)} className="text-red-400 hover:text-red-300 text-xs">
                            Delete
                          </button>
                        </div>
                      </div>
                    ))
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="flex-1 relative">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onNodeDragStop={onNodeDragStop}
              nodeTypes={nodeTypes}
              fitView
              className="bg-slate-900"
            >
              <Background color="#8b5cf6" gap={16} />
              <Controls />
              <MiniMap />
            </ReactFlow>
          </div>
        </div>
      )}

      {/* FAQ Management Tab */}
      {activeTab === "faq" && (
        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-4xl mx-auto">
            <button
              onClick={() => {
                setShowFaqForm(true);
                setEditingFaq(null);
                setFaqForm({ question: "", answer: "", order: "0", is_active: true });
              }}
              className="mb-6 px-6 py-3 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
            >
              + Add New FAQ
            </button>

            {showFaqForm && (
              <div className="mb-6 bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4">
                  {editingFaq ? "Edit FAQ" : "Create New FAQ"}
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-purple-200 mb-2">Question *</label>
                    <input
                      type="text"
                      value={faqForm.question}
                      onChange={(e) => setFaqForm({...faqForm, question: e.target.value})}
                      className="w-full px-4 py-2 bg-white/5 border border-purple-300/30 rounded-lg text-white"
                      placeholder="Enter the question..."
                    />
                  </div>
                  <div>
                    <label className="block text-purple-200 mb-2">Answer *</label>
                    <textarea
                      value={faqForm.answer}
                      onChange={(e) => setFaqForm({...faqForm, answer: e.target.value})}
                      className="w-full px-4 py-2 bg-white/5 border border-purple-300/30 rounded-lg text-white"
                      rows="4"
                      placeholder="Enter the answer..."
                    />
                  </div>
                  <div className="flex gap-4">
                    <div className="flex-1">
                      <label className="block text-purple-200 mb-2">Order</label>
                      <input
                        type="text"
                        value={faqForm.order}
                        onChange={(e) => setFaqForm({...faqForm, order: e.target.value})}
                        className="w-full px-4 py-2 bg-white/5 border border-purple-300/30 rounded-lg text-white"
                      />
                    </div>
                    <div className="flex items-end">
                      <label className="flex items-center gap-2 text-purple-200">
                        <input
                          type="checkbox"
                          checked={faqForm.is_active}
                          onChange={(e) => setFaqForm({...faqForm, is_active: e.target.checked})}
                          className="w-5 h-5"
                        />
                        Active
                      </label>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={() => editingFaq ? updateFaq(editingFaq) : createFaq()}
                      className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition-colors"
                    >
                      {editingFaq ? "Update FAQ" : "Create FAQ"}
                    </button>
                    <button
                      onClick={() => {
                        setShowFaqForm(false);
                        setEditingFaq(null);
                      }}
                      className="flex-1 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-semibold transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-4">
              {faqs.map((faq) => (
                <div key={faq.id} className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                  <div className="flex items-start justify-between mb-3">
                    <h4 className="text-lg font-bold text-white flex-1">{faq.question}</h4>
                    <div className="flex gap-2">
                      {!faq.is_active && (
                        <span className="px-2 py-1 bg-red-500 text-white text-xs rounded">Inactive</span>
                      )}
                      <button
                        onClick={() => startEditFaq(faq)}
                        className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded transition-colors"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => deleteFaq(faq.id)}
                        className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-sm rounded transition-colors"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                  <p className="text-purple-100">{faq.answer}</p>
                  <div className="mt-2 text-xs text-purple-300">Order: {faq.order}</div>
                </div>
              ))}
              {faqs.length === 0 && (
                <div className="text-center py-12 text-purple-300">
                  No FAQs yet. Create your first FAQ above!
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* RAG Document Upload Tab */}
      {activeTab === "rag" && (
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
      )}

      {/* Chat History Tab */}
      {activeTab === "history" && (
        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-white mb-4">Chat Sessions</h2>
            <div className="space-y-3">
              {sessions.map((s) => (
                <div key={s.session_id} className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-purple-200">Session</div>
                      <div className="text-white font-mono text-sm">{s.session_id}</div>
                      <div className="text-xs text-purple-300 mt-1">
                        Messages: {s.message_count} • Last: {new Date(s.last_message_at).toLocaleString()}
                      </div>
                    </div>
                    <button
                      onClick={() => toggleSession(s.session_id)}
                      className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm"
                    >
                      {expandedSessions[s.session_id] ? "Hide" : "View"}
                    </button>
                  </div>

                  {expandedSessions[s.session_id] && (
                    <div className="mt-4 space-y-2">
                      {(messagesBySession[s.session_id] || []).map((m) => (
                        <div key={m.id} className="bg-purple-900/30 px-3 py-2 rounded-lg">
                          <div className="flex items-center justify-between">
                            <span className={`text-xs font-semibold ${m.sender === 'user' ? 'text-blue-200' : 'text-green-200'}`}>{m.sender.toUpperCase()}</span>
                            <span className="text-xs text-purple-300">{new Date(m.created_at).toLocaleString()}</span>
                          </div>
                          <div className="mt-1 text-sm text-purple-100 break-words">{m.message_text}</div>
                        </div>
                      ))}
                      {(!messagesBySession[s.session_id] || messagesBySession[s.session_id].length === 0) && (
                        <div className="text-purple-300 text-sm">No messages in this session.</div>
                      )}
                    </div>
                  )}
                </div>
              ))}
              {sessions.length === 0 && (
                <div className="text-center py-12 text-purple-300">No sessions yet.</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Wrap with ProtectedRoute to require admin access
export default function ProtectedAdminPage() {
  return (
    <ProtectedRoute requireAdmin={true}>
      <AdminPanel />
    </ProtectedRoute>
  );
}
