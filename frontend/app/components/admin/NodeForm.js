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
    <div className="mt-6 bg-white rounded-xl p-4 border border-[#E5E7EB] shadow-md">
      <h3 className="text-lg font-bold text-[#1F2937] mb-4">
        {isEditing ? "Edit Node" : "Create New Node"}
      </h3>
      <div className="space-y-3">
        <div>
          <label className="block text-[#1F2937] mb-1 text-sm font-medium">Message Text *</label>
          <textarea
            value={nodeForm.message_text}
            onChange={(e) => setNodeForm({...nodeForm, message_text: e.target.value})}
            className="w-full px-3 py-2 bg-white border border-[#E5E7EB] rounded-xl text-[#1F2937] text-sm focus:outline-none focus:ring-2 focus:ring-[#4F6BED] focus:border-transparent transition-all duration-200"
            rows="3"
          />
        </div>
        <div>
          <label className="block text-[#1F2937] mb-1 text-sm font-medium">Trigger Text</label>
          <input
            type="text"
            value={nodeForm.trigger_text}
            onChange={(e) => setNodeForm({...nodeForm, trigger_text: e.target.value})}
            className="w-full px-3 py-2 bg-white border border-[#E5E7EB] rounded-xl text-[#1F2937] text-sm focus:outline-none focus:ring-2 focus:ring-[#4F6BED] focus:border-transparent transition-all duration-200"
          />
        </div>
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={nodeForm.is_entry}
            onChange={(e) => setNodeForm({...nodeForm, is_entry: e.target.checked})}
            className="w-4 h-4"
          />
          <label className="text-[#1F2937] text-sm">Is Entry Node</label>
        </div>
        <div className="flex gap-2">
          <button
            onClick={onSubmit}
            className="flex-1 px-4 py-2 bg-[#2CB1A6] hover:bg-[#239B91] text-white rounded-xl font-semibold transition-all duration-200 text-sm shadow-md"
          >
            {isEditing ? "Update" : "Create"}
          </button>
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-2 bg-[#6B7280] hover:bg-[#4B5563] text-white rounded-xl font-semibold transition-all duration-200 text-sm shadow-md"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
