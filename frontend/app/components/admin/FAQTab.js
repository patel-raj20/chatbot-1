/**
 * FAQ Tab Component
 * =================
 * FAQ management interface
 */

import FAQForm from './FAQForm';

export default function FAQTab({ 
  faqs, 
  showFaqForm,
  editingFaq,
  faqForm,
  setFaqForm,
  handleAddFaq,
  handleCancelForm,
  handleSubmitForm,
  startEditFaq,
  deleteFaq
}) {
  return (
    <div className="flex-1 overflow-y-auto p-8 bg-[#F5F7FA]">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={handleAddFaq}
          className="mb-6 px-6 py-3 bg-[#4F6BED] hover:bg-[#3D56D9] text-white rounded-xl font-semibold shadow-md hover:shadow-lg transition-all duration-200"
        >
          + Add New FAQ
        </button>

        {showFaqForm && (
          <FAQForm
            faqForm={faqForm}
            setFaqForm={setFaqForm}
            onSubmit={handleSubmitForm}
            onCancel={handleCancelForm}
            isEditing={!!editingFaq}
          />
        )}

        <div className="space-y-4">
          {faqs.map((faq) => (
            <div key={faq.id} className="bg-white rounded-xl p-6 border border-[#E5E7EB] shadow-md">
              <div className="flex items-start justify-between mb-3">
                <h4 className="text-lg font-bold text-[#1F2937] flex-1">{faq.question}</h4>
                <div className="flex gap-2">
                  {!faq.is_active && (
                    <span className="px-2 py-1 bg-[#E5533D] text-white text-xs rounded-lg">Inactive</span>
                  )}
                  <button
                    onClick={() => startEditFaq(faq)}
                    className="px-3 py-1 bg-[#4F6BED] hover:bg-[#3D56D9] text-white text-sm rounded-lg transition-all duration-200"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => deleteFaq(faq.id)}
                    className="px-3 py-1 bg-[#E5533D] hover:bg-[#CC3F2B] text-white text-sm rounded-lg transition-all duration-200"
                  >
                    Delete
                  </button>
                </div>
              </div>
              <p className="text-[#6B7280]">{faq.answer}</p>
              <div className="mt-2 text-xs text-[#9CA3AF]">Order: {faq.order}</div>
            </div>
          ))}
          {faqs.length === 0 && (
            <div className="text-center py-12 text-[#6B7280]">
              No FAQs yet. Create your first FAQ above!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
