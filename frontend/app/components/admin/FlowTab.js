/**
 * Flow Tab Component
 * ==================
 * ReactFlow editor for conversation trees
 */

import ReactFlow, {
  Background,
  Controls,
  MiniMap,
} from "reactflow";
import "reactflow/dist/style.css";
import CustomNode from './CustomNode';
import NodeForm from './NodeForm';

const nodeTypes = {
  custom: CustomNode,
};

export default function FlowTab({ 
  nodes, 
  edges, 
  onNodesChange, 
  onEdgesChange, 
  onConnect, 
  onNodeDragStop,
  backendNodes,
  backendEdges,
  showNodeForm,
  selectedNode,
  nodeForm,
  setNodeForm,
  handleAddNode,
  handleCancelForm,
  handleSubmitForm,
  deleteEdge
}) {
  return (
    <div className="flex flex-1 overflow-hidden">
      <div className="w-96 bg-white border-r border-[#E5E7EB] overflow-y-auto">
        <div className="p-6">
          <button
            onClick={handleAddNode}
            className="w-full px-6 py-3 bg-[#4F6BED] hover:bg-[#3D56D9] text-white rounded-xl font-semibold shadow-md hover:shadow-lg transition-all duration-200"
          >
            + Add New Node
          </button>

          {(showNodeForm || selectedNode) && (
            <NodeForm
              nodeForm={nodeForm}
              setNodeForm={setNodeForm}
              onSubmit={handleSubmitForm}
              onCancel={handleCancelForm}
              isEditing={!!selectedNode}
            />
          )}

          <div className="mt-6 bg-[#F5F7FA] rounded-xl p-4 border border-[#E5E7EB] shadow-md">
            <h3 className="text-lg font-bold text-[#1F2937] mb-4">Connections ({backendEdges.length})</h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {backendNodes.map(node => (
                node.outgoing_edges.map(edge => (
                  <div key={edge.id} className="bg-white px-3 py-2 rounded-lg border border-[#E5E7EB]">
                    <div className="text-xs text-[#6B7280] mb-1">
                      {node.message_text.substring(0, 30)}... →
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-[#1F2937]">{edge.option_text || "(auto)"}</span>
                      <button onClick={() => deleteEdge(edge.id)} className="text-[#E5533D] hover:text-[#CC3F2B] text-xs">
                        Delete
                      </button>
                    </div>
                  </div>
                ))
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeDragStop={onNodeDragStop}
          nodeTypes={nodeTypes}
          fitView
          className="bg-[#F5F7FA]"
        >
          <Background color="#9CA3AF" gap={16} />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  );
}
