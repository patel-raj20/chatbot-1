/**
 * Custom Node Component for ReactFlow
 * ===================================
 * Visual node representation in flow editor
 */

import { Handle, Position } from "reactflow";

export default function CustomNode({ data }) {
  return (
    <div className="px-4 py-3 rounded-lg bg-white border-2 border-purple-500 shadow-lg min-w-[200px] max-w-[300px]">
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 !bg-purple-500"
      />
      
      {data.is_entry && (
        <div className="mb-2">
          <span className="px-2 py-1 bg-green-500 text-white text-xs font-semibold rounded-full">
            ENTRY
          </span>
        </div>
      )}
      {data.trigger_text && (
        <div className="text-xs text-purple-600 mb-1 font-mono bg-purple-50 px-2 py-1 rounded">
          Trigger: {data.trigger_text}
        </div>
      )}
      <div className="text-sm text-gray-800 font-medium break-words">{data.message_text}</div>
      <div className="mt-2 flex gap-1 flex-wrap">
        <button
          onClick={(e) => {
            e.stopPropagation();
            data.onEdit();
          }}
          className="px-2 py-1 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded transition-colors"
        >
          Edit
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            data.onDelete();
          }}
          className="px-2 py-1 bg-red-500 hover:bg-red-600 text-white text-xs rounded transition-colors"
        >
          Delete
        </button>
      </div>
      <div className="mt-2 text-xs text-gray-500 italic">
        💡 Drag from right edge →
      </div>
      
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 !bg-purple-500"
      />
    </div>
  );
}
