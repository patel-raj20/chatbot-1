/**
 * Node Form Component
 * ==================
 * Form for creating/editing conversation tree nodes
 */

export default function NodeForm({ 
  nodeForm, 
  setNodeForm, 
  onSubmit, 
  onCancel, 
  isEditing = false 
}) {
  return (
    <div className="mt-6 bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20">
      <h3 className="text-lg font-bold text-white mb-4">
        {isEditing ? "Edit Node" : "Create New Node"}
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
            onClick={onSubmit}
            className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition-colors text-sm"
          >
            {isEditing ? "Update" : "Create"}
          </button>
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-semibold transition-colors text-sm"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
