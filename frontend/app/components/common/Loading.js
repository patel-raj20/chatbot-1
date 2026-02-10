/**
 * Loading Component
 * ================
 * Displays a loading spinner with optional message
 */

import { GRADIENTS } from '../../constants/styles';

export default function Loading({ message = "Loading..." }) {
  return (
    <div className={`min-h-screen flex items-center justify-center ${GRADIENTS.primary}`}>
      <div className="text-white text-xl">{message}</div>
    </div>
  );
}
