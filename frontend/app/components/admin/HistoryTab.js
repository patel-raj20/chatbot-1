/**
 * History Tab Component
 * =====================
 * Chat history viewer
 */

export default function HistoryTab({ 
  sessions, 
  expandedSessions, 
  messagesBySession, 
  toggleSession 
}) {
  return (
    <div className="flex-1 overflow-y-auto p-8 bg-[#F5F7FA]">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-[#1F2937] mb-4">Chat Sessions</h2>
        <div className="space-y-3">
          {sessions.map((s) => (
            <div key={s.session_id} className="bg-white rounded-xl p-4 border border-[#E5E7EB] shadow-md">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-[#6B7280]">Session</div>
                  <div className="text-[#1F2937] font-mono text-sm">{s.session_id}</div>
                  <div className="text-xs text-[#9CA3AF] mt-1">
                    Messages: {s.message_count} • Last: {new Date(s.last_message_at).toLocaleString()}
                  </div>
                </div>
                <button
                  onClick={() => toggleSession(s.session_id)}
                  className="px-3 py-1 bg-[#4F6BED] hover:bg-[#3D56D9] text-white rounded-lg text-sm transition-all duration-200"
                >
                  {expandedSessions[s.session_id] ? "Hide" : "View"}
                </button>
              </div>

              {expandedSessions[s.session_id] && (
                <div className="mt-4 space-y-2">
                  {(messagesBySession[s.session_id] || []).map((m) => (
                    <div key={m.id} className="bg-[#F5F7FA] px-3 py-2 rounded-lg border border-[#E5E7EB]">
                      <div className="flex items-center justify-between">
                        <span className={`text-xs font-semibold ${m.sender === 'user' ? 'text-[#2CB1A6]' : 'text-[#4F6BED]'}`}>
                          {m.sender.toUpperCase()}
                        </span>
                        <span className="text-xs text-[#9CA3AF]">{new Date(m.created_at).toLocaleString()}</span>
                      </div>
                      <div className="mt-1 text-sm text-[#6B7280] break-words">{m.message_text}</div>
                    </div>
                  ))}
                  {(!messagesBySession[s.session_id] || messagesBySession[s.session_id].length === 0) && (
                    <div className="text-[#6B7280] text-sm">No messages in this session.</div>
                  )}
                </div>
              )}
            </div>
          ))}
          {sessions.length === 0 && (
            <div className="text-center py-12 text-[#6B7280]">No sessions yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}
