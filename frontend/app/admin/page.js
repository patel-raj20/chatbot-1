/**
 * Admin Panel (Protected)
 * ========================
 * Comprehensive admin interface for managing the chatbot.
 * 
 * AUTHENTICATION:
 *   - Requires admin role
 *   - Redirects to /auth/login if not authenticated
 *   - Redirects to /chatbot if authenticated but not admin
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

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthGuard } from "../lib/authGuard";
import { logout } from "../lib/auth";
import { useAdminFlow } from "../hooks/useAdminFlow";
import { useAdminFAQ } from "../hooks/useAdminFAQ";
import { useAdminHistory } from "../hooks/useAdminHistory";
import { useAdminRAG } from "../hooks/useAdminRAG";
import { GRADIENTS } from "../constants/styles";
import Loading from "../components/common/Loading";
import AdminHeader from "../components/admin/AdminHeader";
import AdminTabs from "../components/admin/AdminTabs";
import FlowTab from "../components/admin/FlowTab";
import FAQTab from "../components/admin/FAQTab";
import HistoryTab from "../components/admin/HistoryTab";
import RAGTab from "../components/admin/RAGTab";

export default function AdminPanel() {
  const router = useRouter();
  const { loading, user } = useAuthGuard('ADMIN');
  const [activeTab, setActiveTab] = useState("history");
  
  // Custom hooks for each feature
  const flowHook = useAdminFlow();
  const faqHook = useAdminFAQ();
  const historyHook = useAdminHistory();
  const ragHook = useAdminRAG();

  // Fetch data when tab changes
  useEffect(() => {
    if (activeTab === "flow") {
      flowHook.fetchNodes();
    } else if (activeTab === "faq") {
      faqHook.fetchFaqs();
    } else if (activeTab === "history") {
      historyHook.fetchSessions();
    }
  }, [activeTab]);

  // Show loading while auth check is in progress
  if (loading) {
    return <Loading />;
  }

  const handleLogout = () => {
    logout();
    router.push('/auth/login');
  };

  return (
    <div className={`flex flex-col h-screen ${GRADIENTS.admin}`}>
      {/* Header with Tabs */}
      <AdminHeader
        user={user}
        onBackToChat={() => router.push('/chatbot')}
        onLogout={handleLogout}
      />

      {/* Tabs Navigation */}
      <div className="px-4 pb-4">
        <AdminTabs activeTab={activeTab} setActiveTab={setActiveTab} />
      </div>

      {/* Tab Content */}
      {activeTab === "flow" && (
        <FlowTab
          nodes={flowHook.nodes}
          edges={flowHook.edges}
          onNodesChange={flowHook.onNodesChange}
          onEdgesChange={flowHook.onEdgesChange}
          onConnect={flowHook.onConnect}
          onNodeDragStop={flowHook.onNodeDragStop}
          backendNodes={flowHook.backendNodes}
          backendEdges={flowHook.backendEdges}
          showNodeForm={flowHook.showNodeForm}
          selectedNode={flowHook.selectedNode}
          nodeForm={flowHook.nodeForm}
          setNodeForm={flowHook.setNodeForm}
          handleAddNode={flowHook.handleAddNode}
          handleCancelForm={flowHook.handleCancelForm}
          handleSubmitForm={flowHook.handleSubmitForm}
          deleteEdge={flowHook.deleteEdge}
        />
      )}

      {activeTab === "faq" && (
        <FAQTab
          faqs={faqHook.faqs}
          showFaqForm={faqHook.showFaqForm}
          editingFaq={faqHook.editingFaq}
          faqForm={faqHook.faqForm}
          setFaqForm={faqHook.setFaqForm}
          handleAddFaq={faqHook.handleAddFaq}
          handleCancelForm={faqHook.handleCancelForm}
          handleSubmitForm={faqHook.handleSubmitForm}
          startEditFaq={faqHook.startEditFaq}
          deleteFaq={faqHook.deleteFaq}
        />
      )}

      {activeTab === "rag" && (
        <RAGTab
          uploadStatus={ragHook.uploadStatus}
          isUploading={ragHook.isUploading}
          handleFileUpload={ragHook.handleFileUpload}
        />
      )}

      {activeTab === "history" && (
        <HistoryTab
          sessions={historyHook.sessions}
          expandedSessions={historyHook.expandedSessions}
          messagesBySession={historyHook.messagesBySession}
          toggleSession={historyHook.toggleSession}
        />
      )}
    </div>
  );
}
