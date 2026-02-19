/**
 * Workflow Questions Section Component
 * ====================================
 * Displays workflow entry questions as cards on chatbot load
 */

export default function WorkflowQuestionsSection({ 
  workflowQuestions, 
  onQuestionClick, 
  isDisabled 
}) {
  if (!workflowQuestions || workflowQuestions.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-xl px-8 py-6 mb-6 border border-[#E5E7EB] shadow-md">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-base font-semibold text-[#1F2937]">How can I help you?</span>
        <span className="text-xs text-[#6B7280] font-medium">Choose a topic</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {workflowQuestions.map((question) => (
          <button
            key={question.id}
            onClick={() => onQuestionClick(question.trigger_text)}
            disabled={isDisabled}
            className="group bg-[#F5F7FA] hover:bg-[#4F6BED] text-[#1F2937] hover:text-white px-6 py-3.5 rounded-xl text-sm font-medium border border-[#E5E7EB] hover:border-[#4F6BED] shadow-sm hover:shadow-md transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed text-left"
          >
            {question.trigger_text}
          </button>
        ))}
      </div>
    </div>
  );
}
