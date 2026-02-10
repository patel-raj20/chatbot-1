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
                        <span className={`text-xs font-semibold ${m.sender === 'user' ? 'text-blue-200' : 'text-green-200'}`}>
                          {m.sender.toUpperCase()}
                        </span>
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
  );
}
