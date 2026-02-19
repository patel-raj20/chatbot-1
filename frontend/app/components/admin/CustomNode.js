/**
 * Custom Node Component for ReactFlow
 * ===================================
 * Visual node representation in flow editor
 */

import { Handle, Position } from "reactflow";

export default function CustomNode({ data }) {
  return (
    <div className="px-4 py-3 rounded-xl bg-white border-2 border-[#4F6BED] shadow-md min-w-[200px] max-w-[300px]">
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 !bg-[#4F6BED]"
      />
      
      {data.is_entry && (
        <div className="mb-2">
          <span className="px-2 py-1 bg-[#2CB1A6] text-white text-xs font-semibold rounded-full">
            ENTRY
          </span>
        </div>
      )}
      {data.trigger_text && (
        <div className="text-xs text-[#4F6BED] mb-1 font-mono bg-[#EEF2FF] px-2 py-1 rounded-lg">
          Trigger: {data.trigger_text}
        </div>
      )}
      <div className="text-sm text-[#1F2937] font-medium break-words">{data.message_text}</div>
      <div className="mt-2 flex gap-1 flex-wrap">
        <button
          onClick={(e) => {
            e.stopPropagation();
            data.onEdit();
          }}
          className="px-2 py-1 bg-[#4F6BED] hover:bg-[#3D56D9] text-white text-xs rounded-lg transition-all duration-200"
        >
          Edit
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            data.onDelete();
          }}
          className="px-2 py-1 bg-[#E5533D] hover:bg-[#CC3F2B] text-white text-xs rounded-lg transition-all duration-200"
        >
          Delete
        </button>
      </div>
      <div className="mt-2 text-xs text-[#9CA3AF] italic">
        💡 Drag from right edge →
      </div>
      
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 !bg-[#4F6BED]"
      />
    </div>
  );
}
