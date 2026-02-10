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
          className={`px-6 py-3 rounded-lg font-semibold transition-all ${
            activeTab === tab.id
              ? "bg-purple-600 text-white shadow-lg"
              : "bg-white/10 text-purple-200 hover:bg-white/20"
          }`}
        >
          {tab.icon} {tab.label}
        </button>
      ))}
    </div>
  );
}
