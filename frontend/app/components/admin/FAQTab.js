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
    <div className="flex-1 overflow-y-auto p-8">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={handleAddFaq}
          className="mb-6 px-6 py-3 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
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
            <div key={faq.id} className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="flex items-start justify-between mb-3">
                <h4 className="text-lg font-bold text-white flex-1">{faq.question}</h4>
                <div className="flex gap-2">
                  {!faq.is_active && (
                    <span className="px-2 py-1 bg-red-500 text-white text-xs rounded">Inactive</span>
                  )}
                  <button
                    onClick={() => startEditFaq(faq)}
                    className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded transition-colors"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => deleteFaq(faq.id)}
                    className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-sm rounded transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
              <p className="text-purple-100">{faq.answer}</p>
              <div className="mt-2 text-xs text-purple-300">Order: {faq.order}</div>
            </div>
          ))}
          {faqs.length === 0 && (
            <div className="text-center py-12 text-purple-300">
              No FAQs yet. Create your first FAQ above!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
