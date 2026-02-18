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
    <div className="absolute bottom-full left-0 right-0 mb-2 bg-white rounded-lg shadow-2xl border border-gray-200 max-h-64 overflow-y-auto z-50">
      {isLoading ? (
        <div className="px-4 py-3 text-center text-gray-500 text-sm">
          <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
          <span className="ml-2">Searching...</span>
        </div>
      ) : suggestions.length === 0 ? (
        <div className="px-4 py-3 text-center text-gray-500 text-sm">
          No suggestions found
        </div>
      ) : (
        <>
          <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
            <span className="text-xs font-semibold text-gray-600 uppercase">
              FAQ Suggestions ({suggestions.length})
            </span>
          </div>
          <div className="divide-y divide-gray-100">
            {suggestions.map((faq) => (
              <button
                key={faq.id}
                onClick={() => onSuggestionClick(faq.question)}
                className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors duration-150 group"
              >
                <div className="flex items-start gap-2">
                  <svg 
                    className="w-4 h-4 text-gray-400 group-hover:text-blue-500 mt-0.5 flex-shrink-0" 
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
                  <span className="text-sm text-gray-700 group-hover:text-gray-900">
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
