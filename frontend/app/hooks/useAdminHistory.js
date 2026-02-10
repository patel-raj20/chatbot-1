/**
 * Admin History Hook
 * ==================
 * Custom hook for managing chat history
 */

import { useState } from 'react';
import { API_BASE_URL } from '../constants/api';

export function useAdminHistory() {
  const [sessions, setSessions] = useState([]);
  const [expandedSessions, setExpandedSessions] = useState({});
  const [messagesBySession, setMessagesBySession] = useState({});

  const fetchSessions = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/chat/sessions`);
      const data = await res.json();
      setSessions(data);
    } catch (err) {
      console.error("Failed to fetch sessions:", err);
    }
  };

  const fetchSessionMessages = async (sessionId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/chat/sessions/${sessionId}`);
      const data = await res.json();
      setMessagesBySession(prev => ({ ...prev, [sessionId]: data }));
    } catch (err) {
      console.error("Failed to fetch session messages:", err);
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
