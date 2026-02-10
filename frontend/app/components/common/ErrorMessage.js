/**
 * Error Message Component
 * ======================
 * Displays error messages in a styled container
 */

export default function ErrorMessage({ error, onClose }) {
  if (!error) return null;

  return (
    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
      <div className="flex items-start justify-between">
        <p>{error}</p>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-4 text-red-500 hover:text-red-700 font-bold"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}
