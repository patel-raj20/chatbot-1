/**
 * FAQ Section Component
 * ====================
 * Displays quick question buttons
 */

export default function FAQSection({ faqs, onFaqClick }) {
  if (faqs.length === 0) return null;

  return (
    <div className="bg-gradient-to-r from-purple-50 to-violet-50 border-t border-purple-100 px-6 py-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-sm font-semibold text-purple-700">Quick Questions</span>
        <span className="text-xs text-purple-500">Click to ask</span>
      </div>
      <div className="flex flex-wrap gap-2 max-h-24 overflow-y-auto">
        {faqs.map((faq) => (
          <button
            key={faq.id}
            onClick={() => onFaqClick(faq.question)}
            className="group relative overflow-hidden bg-white hover:bg-gradient-to-r hover:from-violet-500 hover:to-purple-500 text-purple-700 hover:text-white px-4 py-2 rounded-full text-sm font-medium border-2 border-purple-200 hover:border-transparent shadow-md hover:shadow-lg transform hover:scale-105 transition-all duration-300"
          >
            <span className="relative z-10">{faq.question}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
