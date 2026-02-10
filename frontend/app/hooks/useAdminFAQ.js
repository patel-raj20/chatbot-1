/**
 * Admin FAQ Hook
 * ==============
 * Custom hook for managing FAQs
 */

import { useState } from 'react';
import { API_BASE_URL } from '../constants/api';

export function useAdminFAQ() {
  const [faqs, setFaqs] = useState([]);
  const [showFaqForm, setShowFaqForm] = useState(false);
  const [editingFaq, setEditingFaq] = useState(null);
  const [faqForm, setFaqForm] = useState({
    question: "",
    answer: "",
    order: "0",
    is_active: true
  });

  const fetchFaqs = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/faqs`);
      const data = await res.json();
      setFaqs(data);
    } catch (err) {
      console.error("Failed to fetch FAQs:", err);
    }
  };

  const createFaq = async () => {
    try {
      await fetch(`${API_BASE_URL}/admin/faqs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(faqForm)
      });
      setFaqForm({ question: "", answer: "", order: "0", is_active: true });
      setShowFaqForm(false);
      fetchFaqs();
    } catch (err) {
      console.error("Failed to create FAQ:", err);
    }
  };

  const updateFaq = async (faqId) => {
    try {
      await fetch(`${API_BASE_URL}/admin/faqs/${faqId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(faqForm)
      });
      setFaqForm({ question: "", answer: "", order: "0", is_active: true });
      setEditingFaq(null);
      fetchFaqs();
    } catch (err) {
      console.error("Failed to update FAQ:", err);
    }
  };

  const deleteFaq = async (faqId) => {
    if (!confirm("Delete this FAQ?")) return;
    
    try {
      await fetch(`${API_BASE_URL}/admin/faqs/${faqId}`, {
        method: "DELETE"
      });
      fetchFaqs();
    } catch (err) {
      console.error("Failed to delete FAQ:", err);
    }
  };

  const startEditFaq = (faq) => {
    setEditingFaq(faq.id);
    setFaqForm({
      question: faq.question,
      answer: faq.answer,
      order: faq.order,
      is_active: faq.is_active
    });
    setShowFaqForm(true);
  };

  const handleAddFaq = () => {
    setShowFaqForm(true);
    setEditingFaq(null);
    setFaqForm({ question: "", answer: "", order: "0", is_active: true });
  };

  const handleCancelForm = () => {
    setShowFaqForm(false);
    setEditingFaq(null);
  };

  const handleSubmitForm = () => {
    if (editingFaq) {
      updateFaq(editingFaq);
    } else {
      createFaq();
    }
  };

  return {
    faqs,
    showFaqForm,
    editingFaq,
    faqForm,
    setFaqForm,
    fetchFaqs,
    deleteFaq,
    startEditFaq,
    handleAddFaq,
    handleCancelForm,
    handleSubmitForm
  };
}
