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
      <div className="w-96 bg-slate-900/50 backdrop-blur-lg border-r border-white/10 overflow-y-auto">
        <div className="p-6">
          <button
            onClick={handleAddNode}
            className="w-full px-6 py-3 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
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

          <div className="mt-6 bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20">
            <h3 className="text-lg font-bold text-white mb-4">Connections ({backendEdges.length})</h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {backendNodes.map(node => (
                node.outgoing_edges.map(edge => (
                  <div key={edge.id} className="bg-purple-900/30 px-3 py-2 rounded-lg">
                    <div className="text-xs text-purple-100 mb-1">
                      {node.message_text.substring(0, 30)}... →
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-purple-300">{edge.option_text || "(auto)"}</span>
                      <button onClick={() => deleteEdge(edge.id)} className="text-red-400 hover:text-red-300 text-xs">
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
          className="bg-slate-900"
        >
          <Background color="#8b5cf6" gap={16} />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  );
}
