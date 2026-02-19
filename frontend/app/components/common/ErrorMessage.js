/**
 * Error Message Component
 * ======================
 * Displays error messages in a styled container
 */

export default function ErrorMessage({ error, onClose }) {
  if (!error) return null;

  return (
    <div className="bg-red-50 border border-[#E5533D] text-[#E5533D] px-4 py-3 rounded-xl">
      <div className="flex items-start justify-between">
        <p>{error}</p>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-4 text-[#E5533D] hover:text-[#CC3F2B] font-bold"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}
