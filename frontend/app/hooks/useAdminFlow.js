/**
 * Admin Flow Hook
 * ===============
 * Custom hook for managing conversation flow editor
 */

import { useState, useCallback } from 'react';
import { useNodesState, useEdgesState, MarkerType } from 'reactflow';
import { API_BASE_URL, getAuthHeaders } from '../lib/api';
import { getToken } from '../lib/auth';

export function useAdminFlow() {
  const [backendNodes, setBackendNodes] = useState([]);
  const [backendEdges, setBackendEdges] = useState([]);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showNodeForm, setShowNodeForm] = useState(false);
  const [nodeForm, setNodeForm] = useState({
    message_text: "",
    trigger_text: "",
    is_entry: false,
    position_x: 250,
    position_y: 100
  });

  const fetchNodes = async () => {
    // Verify token exists before making request
    const token = getToken();
    if (!token) {
      console.error('No authentication token found');
      setBackendNodes([]);
      setNodes([]);
      setEdges([]);
      return;
    }
    
    try {
      const res = await fetch(`${API_BASE_URL}/admin/nodes`, {
        headers: getAuthHeaders()
      });
      
      if (!res.ok) {
        console.error(`Failed to fetch nodes: ${res.status} ${res.statusText}`);
        setBackendNodes([]);
        setNodes([]);
        setEdges([]);
        return;
      }
      
      const data = await res.json();
      setBackendNodes(Array.isArray(data) ? data : []);
      convertToFlowNodes(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to fetch nodes:", err);
      setBackendNodes([]);
      setNodes([]);
      setEdges([]);
    }
  };

  const convertToFlowNodes = (backendData) => {
    const flowNodes = backendData.map((node, index) => ({
      id: node.id,
      type: "custom",
      position: { 
        x: node.position_x || (index % 3) * 350, 
        y: node.position_y || Math.floor(index / 3) * 200 
      },
      data: {
        message_text: node.message_text,
        trigger_text: node.trigger_text,
        is_entry: node.is_entry,
        onEdit: () => startEdit(node),
        onDelete: () => deleteNode(node.id),
      },
      sourcePosition: 'right',
      targetPosition: 'left',
    }));

    const flowEdges = [];
    backendData.forEach((node) => {
      node.outgoing_edges.forEach((edge) => {
        flowEdges.push({
          id: edge.id,
          source: node.id,
          target: edge.to_node_id,
          label: edge.option_text || "auto",
          type: "smoothstep",
          animated: !edge.option_text,
          markerEnd: {
            type: MarkerType.ArrowClosed,
            width: 20,
            height: 20,
            color: "#9333ea",
          },
          style: {
            stroke: "#9333ea",
            strokeWidth: 2,
          },
        });
      });
    });

    setNodes(flowNodes);
    setEdges(flowEdges);
    
    const allEdges = [];
    backendData.forEach(node => {
      allEdges.push(...node.outgoing_edges);
    });
    setBackendEdges(allEdges);
  };

  const onConnect = useCallback(
    async (params) => {
      const optionText = prompt("Enter option text for this connection (or leave empty for auto-transition):");
      if (optionText === null) return;
      
      try {
        await fetch(`${API_BASE_URL}/admin/edges`, {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            from_node_id: params.source,
            to_node_id: params.target,
            option_text: optionText || null
          })
        });
        fetchNodes();
      } catch (err) {
        console.error("Failed to create edge:", err);
      }
    },
    []
  );

  const onNodeDragStop = useCallback(
    async (event, node) => {
      try {
        await fetch(`${API_BASE_URL}/admin/nodes/${node.id}`, {
          method: "PUT",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            position_x: node.position.x,
            position_y: node.position.y,
          }),
        });
      } catch (err) {
        console.error("Failed to update node position:", err);
      }
    },
    []
  );

  const createNode = async () => {
    try {
      await fetch(`${API_BASE_URL}/admin/nodes`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(nodeForm)
      });
      setNodeForm({ message_text: "", trigger_text: "", is_entry: false, position_x: 250, position_y: 100 });
      setShowNodeForm(false);
      fetchNodes();
    } catch (err) {
      console.error("Failed to create node:", err);
    }
  };

  const updateNode = async (nodeId) => {
    try {
      await fetch(`${API_BASE_URL}/admin/nodes/${nodeId}`, {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify(nodeForm)
      });
      setNodeForm({ message_text: "", trigger_text: "", is_entry: false, position_x: 250, position_y: 100 });
      setSelectedNode(null);
      fetchNodes();
    } catch (err) {
      console.error("Failed to update node:", err);
    }
  };

  const deleteNode = async (nodeId) => {
    if (!confirm("Delete this node and all its connections?")) return;
    
    try {
      await fetch(`${API_BASE_URL}/admin/nodes/${nodeId}`, {
        method: "DELETE",
        headers: getAuthHeaders()
      });
      fetchNodes();
    } catch (err) {
      console.error("Failed to delete node:", err);
    }
  };

  const deleteEdge = async (edgeId) => {
    if (!confirm("Delete this connection?")) return;
    
    try {
      await fetch(`${API_BASE_URL}/admin/edges/${edgeId}`, {
        method: "DELETE",
        headers: getAuthHeaders()
      });
      fetchNodes();
    } catch (err) {
      console.error("Failed to delete edge:", err);
    }
  };

  const startEdit = (node) => {
    setSelectedNode(node.id);
    setNodeForm({
      message_text: node.message_text,
      trigger_text: node.trigger_text || "",
      is_entry: node.is_entry,
      position_x: node.position_x || 250,
      position_y: node.position_y || 100
    });
  };

  const handleAddNode = () => {
    setShowNodeForm(true);
    setSelectedNode(null);
    setNodeForm({ message_text: "", trigger_text: "", is_entry: false, position_x: 250, position_y: 100 });
  };

  const handleCancelForm = () => {
    setShowNodeForm(false);
    setSelectedNode(null);
  };

  const handleSubmitForm = () => {
    if (selectedNode) {
      updateNode(selectedNode);
    } else {
      createNode();
    }
  };

  return {
    backendNodes,
    backendEdges,
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    selectedNode,
    showNodeForm,
    nodeForm,
    setNodeForm,
    fetchNodes,
    onConnect,
    onNodeDragStop,
    deleteEdge,
    handleAddNode,
    handleCancelForm,
    handleSubmitForm
  };
}
