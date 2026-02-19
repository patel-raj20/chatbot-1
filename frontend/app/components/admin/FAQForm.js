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
    <div className="mb-6 bg-white rounded-xl p-6 border border-[#E5E7EB] shadow-md">
      <h3 className="text-xl font-bold text-[#1F2937] mb-4">
        {isEditing ? "Edit FAQ" : "Create New FAQ"}
      </h3>
      <div className="space-y-4">
        <div>
          <label className="block text-[#1F2937] mb-2 font-medium">Question *</label>
          <input
            type="text"
            value={faqForm.question}
            onChange={(e) => setFaqForm({...faqForm, question: e.target.value})}
            className="w-full px-4 py-2 bg-white border border-[#E5E7EB] rounded-xl text-[#1F2937] focus:outline-none focus:ring-2 focus:ring-[#4F6BED] focus:border-transparent transition-all duration-200"
            placeholder="Enter the question..."
          />
        </div>
        <div>
          <label className="block text-[#1F2937] mb-2 font-medium">Answer *</label>
          <textarea
            value={faqForm.answer}
            onChange={(e) => setFaqForm({...faqForm, answer: e.target.value})}
            className="w-full px-4 py-2 bg-white border border-[#E5E7EB] rounded-xl text-[#1F2937] focus:outline-none focus:ring-2 focus:ring-[#4F6BED] focus:border-transparent transition-all duration-200"
            rows="4"
            placeholder="Enter the answer..."
          />
        </div>
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-[#1F2937] mb-2 font-medium">Order</label>
            <input
              type="text"
              value={faqForm.order}
              onChange={(e) => setFaqForm({...faqForm, order: e.target.value})}
              className="w-full px-4 py-2 bg-white border border-[#E5E7EB] rounded-xl text-[#1F2937] focus:outline-none focus:ring-2 focus:ring-[#4F6BED] focus:border-transparent transition-all duration-200"
            />
          </div>
          <div className="flex items-end">
            <label className="flex items-center gap-2 text-[#1F2937]">
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
            className="flex-1 px-6 py-3 bg-[#2CB1A6] hover:bg-[#239B91] text-white rounded-xl font-semibold transition-all duration-200 shadow-md"
          >
            {isEditing ? "Update FAQ" : "Create FAQ"}
          </button>
          <button
            onClick={onCancel}
            className="flex-1 px-6 py-3 bg-[#6B7280] hover:bg-[#4B5563] text-white rounded-xl font-semibold transition-all duration-200 shadow-md"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
