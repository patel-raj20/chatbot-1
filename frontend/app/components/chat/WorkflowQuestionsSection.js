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
  console.log("WorkflowQuestionsSection - received questions:", workflowQuestions, "count:", workflowQuestions?.length);
  
  if (!workflowQuestions || workflowQuestions.length === 0) {
    return null;
  }

  return (
    <div className="bg-gradient-to-br from-blue-50/50 via-cyan-50/30 to-blue-50/50 rounded-2xl px-8 py-6 mb-6 backdrop-blur-sm">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-base font-semibold text-blue-600">How can I help you?</span>
        <span className="text-xs text-blue-400 font-medium">Choose a topic</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {workflowQuestions.map((question) => (
          <button
            key={question.id}
            onClick={() => onQuestionClick(question.trigger_text)}
            disabled={isDisabled}
            className="group bg-white hover:bg-blue-500 text-blue-600 hover:text-white px-6 py-3.5 rounded-xl text-sm font-medium border border-blue-100 hover:border-blue-500 shadow-sm hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed text-left"
          >
            {question.trigger_text}
          </button>
        ))}
      </div>
    </div>
  );
}
