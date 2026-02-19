/**
 * FAQ Section Component
 * ====================
 * Displays quick question buttons
 */

export default function FAQSection({ faqs, onFaqClick }) {
  if (faqs.length === 0) return null;

  return (
    <div className="bg-[#EEF2FF] border-t border-[#E5E7EB] px-6 py-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-sm font-semibold text-[#4F6BED]">Quick Questions</span>
        <span className="text-xs text-[#6B7280]">Click to ask</span>
      </div>
      <div className="flex flex-wrap gap-2 max-h-24 overflow-y-auto">
        {faqs.map((faq) => (
          <button
            key={faq.id}
            onClick={() => onFaqClick(faq.question)}
            className="bg-white hover:bg-[#4F6BED] text-[#4F6BED] hover:text-white px-4 py-2 rounded-xl text-sm font-medium border-2 border-[#E5E7EB] hover:border-[#4F6BED] shadow-md hover:shadow-lg transition-all duration-200"
          >
            {faq.question}
          </button>
        ))}
      </div>
    </div>
  );
}
