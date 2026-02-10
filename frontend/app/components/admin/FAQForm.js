/**
 * FAQ Form Component
 * ==================
 * Form for creating/editing FAQs
 */

export default function FAQForm({ 
  faqForm, 
  setFaqForm, 
  onSubmit, 
  onCancel, 
  isEditing = false 
}) {
  return (
    <div className="mb-6 bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
      <h3 className="text-xl font-bold text-white mb-4">
        {isEditing ? "Edit FAQ" : "Create New FAQ"}
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
            onClick={onSubmit}
            className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition-colors"
          >
            {isEditing ? "Update FAQ" : "Create FAQ"}
          </button>
          <button
            onClick={onCancel}
            className="flex-1 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-semibold transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
