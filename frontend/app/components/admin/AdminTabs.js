/**
 * Admin Tabs Component
 * ====================
 * Navigation tabs for admin panel
 */

export default function AdminTabs({ activeTab, setActiveTab }) {
  const tabs = [
    { id: "history", icon: "🕘", label: "Chat History" },
    { id: "flow", icon: "🔀", label: "Flow Builder" },
    { id: "faq", icon: "❓", label: "FAQ Management" },
    { id: "rag", icon: "📄", label: "Document Upload" },
  ];

  return (
    <div className="flex gap-2">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => setActiveTab(tab.id)}
          className={`px-6 py-3 rounded-xl font-semibold transition-all duration-200 ${
            activeTab === tab.id
              ? "bg-[#4F6BED] text-white shadow-lg"
              : "bg-white text-[#1F2937] hover:bg-[#F5F7FA] border border-[#E5E7EB] shadow-md"
          }`}
        >
          {tab.icon} {tab.label}
        </button>
      ))}
    </div>
  );
}
