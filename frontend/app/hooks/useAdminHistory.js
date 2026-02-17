/**
 * Admin History Hook
 * ==================
 * Custom hook for managing chat history
 */

import { useState } from 'react';
import { API_BASE_URL, getAuthHeaders } from '../lib/api';
import { getToken } from '../lib/auth';

export function useAdminHistory() {
  const [sessions, setSessions] = useState([]);
  const [expandedSessions, setExpandedSessions] = useState({});
  const [messagesBySession, setMessagesBySession] = useState({});

  const fetchSessions = async () => {
    // Verify token exists before making request
    const token = getToken();
    if (!token) {
      console.error('No authentication token found');
      setSessions([]);
      return;
    }
    
    try {
      const res = await fetch(`${API_BASE_URL}/admin/chat/sessions`, {
        headers: getAuthHeaders()
      });
      
      if (!res.ok) {
        console.error(`Failed to fetch sessions: ${res.status} ${res.statusText}`);
        setSessions([]);
        return;
      }
      
      const data = await res.json();
      setSessions(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to fetch sessions:", err);
      setSessions([]);
    }
  };

  const fetchSessionMessages = async (sessionId) => {
    // Verify token exists before making request
    const token = getToken();
    if (!token) {
      console.error('No authentication token found');
      setMessagesBySession(prev => ({ ...prev, [sessionId]: [] }));
      return;
    }
    
    try {
      const res = await fetch(`${API_BASE_URL}/admin/chat/sessions/${sessionId}`, {
        headers: getAuthHeaders()
      });
      
      if (!res.ok) {
        console.error(`Failed to fetch session messages: ${res.status} ${res.statusText}`);
        setMessagesBySession(prev => ({ ...prev, [sessionId]: [] }));
        return;
      }
      
      const data = await res.json();
      setMessagesBySession(prev => ({ ...prev, [sessionId]: Array.isArray(data) ? data : [] }));
    } catch (err) {
      console.error("Failed to fetch session messages:", err);
      setMessagesBySession(prev => ({ ...prev, [sessionId]: [] }));
    }
  };

  const toggleSession = async (sessionId) => {
    setExpandedSessions(prev => ({ ...prev, [sessionId]: !prev[sessionId] }));
    const willExpand = !expandedSessions[sessionId];
    if (willExpand && !messagesBySession[sessionId]) {
      await fetchSessionMessages(sessionId);
    }
  };

  return {
    sessions,
    expandedSessions,
    messagesBySession,
    fetchSessions,
    toggleSession
  };
}
