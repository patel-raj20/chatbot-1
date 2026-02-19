/**
 * FAQ Suggestions Dropdown Component
 * ==================================
 * Floating dropdown showing FAQ search results while typing
 */

export default function FAQSuggestionsDropdown({ 
  suggestions, 
  onSuggestionClick, 
  isLoading, 
  isVisible 
}) {
  if (!isVisible) return null;

  return (
    <div className="absolute bottom-full left-0 right-0 mb-2 bg-white rounded-xl shadow-2xl border border-[#E5E7EB] max-h-64 overflow-y-auto z-50">
      {isLoading ? (
        <div className="px-4 py-3 text-center text-[#6B7280] text-sm">
          <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-[#4F6BED]"></div>
          <span className="ml-2">Searching...</span>
        </div>
      ) : suggestions.length === 0 ? (
        <div className="px-4 py-3 text-center text-[#6B7280] text-sm">
          No suggestions found
        </div>
      ) : (
        <>
          <div className="px-4 py-2 bg-[#F5F7FA] border-b border-[#E5E7EB]">
            <span className="text-xs font-semibold text-[#6B7280] uppercase">
              FAQ Suggestions ({suggestions.length})
            </span>
          </div>
          <div className="divide-y divide-[#E5E7EB]">
            {suggestions.map((faq) => (
              <button
                key={faq.id}
                onClick={() => onSuggestionClick(faq.question)}
                className="w-full px-4 py-3 text-left hover:bg-[#F5F7FA] transition-all duration-200 group"
              >
                <div className="flex items-start gap-2">
                  <svg 
                    className="w-4 h-4 text-[#9CA3AF] group-hover:text-[#4F6BED] mt-0.5 flex-shrink-0" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2} 
                      d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
                    />
                  </svg>
                  <span className="text-sm text-[#1F2937] group-hover:text-[#4F6BED]">
                    {faq.question}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
