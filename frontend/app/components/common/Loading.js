/**
 * Loading Component
 * ================
 * Displays a loading spinner with optional message
 */

import { GRADIENTS } from '../../constants/styles';

export default function Loading({ message = "Loading..." }) {
  return (
    <div className={`min-h-screen flex items-center justify-center ${GRADIENTS.primary}`}>
      <div className="text-[#1F2937] text-xl flex items-center gap-3">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#4F6BED]"></div>
        {message}
      </div>
    </div>
  );
}
