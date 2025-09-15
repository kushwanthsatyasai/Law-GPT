import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const API_BASE = '/api';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'ai'; content: string }>>([]);
  const [input, setInput] = useState('');
  const [showSidebar, setShowSidebar] = useState(false);
  const historyRef = useRef<HTMLDivElement | null>(null);
  const [recentDocuments, setRecentDocuments] = useState<Array<{ id: number; title: string; date: string; content_type: string }>>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(false);
  const [recentChats, setRecentChats] = useState<Array<{ id: number; title: string; date: string }>>([]);
  const [loadingChats, setLoadingChats] = useState(false);
  const [userInfo, setUserInfo] = useState<{ name: string; email: string } | null>(null);
  const [selectedChat, setSelectedChat] = useState<{ id: number; title: string; messages: Array<{ id: number; role: 'user' | 'assistant'; content: string; created_at: string }> } | null>(null);
  const [chatInput, setChatInput] = useState('');
  const [loadingChat, setLoadingChat] = useState(false);
  const [showNewChatModal, setShowNewChatModal] = useState(false);
  const [newChatTitle, setNewChatTitle] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);
  const [selectedDocument, setSelectedDocument] = useState<{ id: number; title: string } | null>(null);
  const [documentAnalysis, setDocumentAnalysis] = useState<any>(null);
  const [analyzingDocument, setAnalyzingDocument] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [savedAnalyses, setSavedAnalyses] = useState<Array<{ id: number; document_id: number; analysis_type: string; overall_risk_level: string; summary: string; created_at: string }>>([]);
  const [loadingAnalyses, setLoadingAnalyses] = useState(false);

  useEffect(() => {
    if (historyRef.current) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [selectedChat?.messages]);

  useEffect(() => {
    loadDocuments();
    loadChatSessions();
    loadUserInfo();
    loadSavedAnalyses();
  }, []);

  const loadDocuments = async () => {
    setLoadingDocuments(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const res = await fetch(`${API_BASE}/documents`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (res.ok) {
        const documents = await res.json();
        setRecentDocuments(documents.map((doc: any) => ({
          id: doc.id,
          title: doc.title,
          date: new Date(doc.created_at).toLocaleDateString(),
          content_type: doc.content_type
        })));
      }
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setLoadingDocuments(false);
    }
  };

  const loadChatSessions = async () => {
    setLoadingChats(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const res = await fetch(`${API_BASE}/chat/sessions`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (res.ok) {
        const sessions = await res.json();
        setRecentChats(sessions.map((session: any) => ({
          id: session.id,
          title: session.title,
          date: new Date(session.updated_at).toLocaleDateString()
        })));
      }
    } catch (err) {
      console.error('Failed to load chat sessions:', err);
    } finally {
      setLoadingChats(false);
    }
  };

  const loadUserInfo = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const res = await fetch(`${API_BASE}/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (res.ok) {
        const userData = await res.json();
        setUserInfo({
          name: userData.name || userData.email.split('@')[0],
          email: userData.email
        });
        
        // Store user info in localStorage for persistence
        localStorage.setItem('userEmail', userData.email);
        localStorage.setItem('userName', userData.name || userData.email.split('@')[0]);
      }
    } catch (err) {
      console.error('Failed to load user info:', err);
      // Fallback to stored values or defaults
      const userEmail = localStorage.getItem('userEmail') || 'user@example.com';
      const userName = localStorage.getItem('userName') || 'User';
      
      setUserInfo({
        name: userName,
        email: userEmail
      });
    }
  };

  const loadSavedAnalyses = async () => {
    setLoadingAnalyses(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const res = await fetch(`${API_BASE}/document-analyses`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (res.ok) {
        const analyses = await res.json();
        setSavedAnalyses(analyses);
      }
    } catch (err) {
      console.error('Failed to load saved analyses:', err);
    } finally {
      setLoadingAnalyses(false);
    }
  };

  const loadSavedAnalysis = async (analysisId: number) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const res = await fetch(`${API_BASE}/document-analyses/${analysisId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (res.ok) {
        const analysis = await res.json();
        setDocumentAnalysis(analysis);
        setSelectedDocument({ id: analysis.document_id, title: analysis.document_title });
        setShowAnalysisModal(true);
      }
    } catch (err) {
      console.error('Failed to load saved analysis:', err);
    }
  };


  const loadChatSession = async (sessionId: number) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return null;

      const res = await fetch(`${API_BASE}/chat/sessions/${sessionId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (res.ok) {
        const sessionData = await res.json();
        const chatData = {
          id: sessionData.id,
          title: sessionData.title,
          messages: sessionData.messages || []
        };
        setSelectedChat(chatData);
        return chatData;
      }
    } catch (err) {
      console.error('Failed to load chat session:', err);
    }
    return null;
  };

  const createNewChat = async () => {
    if (!newChatTitle.trim()) return;
    
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const res = await fetch(`${API_BASE}/chat/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ title: newChatTitle })
      });

      if (res.ok) {
        const newSession = await res.json();
        setSelectedChat({
          id: newSession.id,
          title: newSession.title,
          messages: []
        });
        setShowNewChatModal(false);
        setNewChatTitle('');
        // Refresh chat sessions list
        loadChatSessions();
      }
    } catch (err) {
      console.error('Failed to create new chat:', err);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim() || !selectedChat) return;
    
    setLoadingChat(true);
    const messageText = chatInput.trim();
    setChatInput('');

    // Add user message immediately
    const userMessage = {
      id: Date.now(),
      role: 'user' as const,
      content: messageText,
      created_at: new Date().toISOString()
    };

    setSelectedChat(prev => prev ? {
      ...prev,
      messages: [...prev.messages, userMessage]
    } : null);

    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const res = await fetch(`${API_BASE}/chat/sessions/${selectedChat.id}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ message: messageText })
      });

      if (res.ok) {
        const response = await res.json();
        const aiMessage = {
          id: response.message_id || Date.now() + 1,
          role: 'assistant' as const,
          content: response.content || 'Sorry, I could not process your message.',
          created_at: new Date().toISOString()
        };

        setSelectedChat(prev => prev ? {
          ...prev,
          messages: [...prev.messages, aiMessage]
        } : null);
      } else {
        throw new Error('Failed to send message');
      }
    } catch (err) {
      console.error('Failed to send message:', err);
      // Add error message
      const errorMessage = {
        id: Date.now() + 2,
        role: 'assistant' as const,
        content: 'Sorry, there was an error processing your message. Please try again.',
        created_at: new Date().toISOString()
      };

      setSelectedChat(prev => prev ? {
        ...prev,
        messages: [...prev.messages, errorMessage]
      } : null);
    } finally {
      setLoadingChat(false);
    }
  };

  const handleChatKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  };

  const closeChat = () => {
    setSelectedChat(null);
  };

  const analyzeDocument = async (documentId: number, documentTitle: string) => {
    setAnalyzingDocument(true);
    setAnalysisError(null);
    setSelectedDocument({ id: documentId, title: documentTitle });
    setShowAnalysisModal(true);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('You must be logged in to analyze documents');
      }

      const response = await fetch(`${API_BASE}/analyze-document`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          document_id: documentId,
          analysis_type: 'comprehensive'
        })
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      setDocumentAnalysis(data);
    } catch (err: any) {
      setAnalysisError('Analysis failed: ' + (err.message || 'Unknown error'));
    } finally {
      setAnalyzingDocument(false);
    }
  };

  const addDocumentToChat = async (documentId: number, documentTitle: string) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      // Create a new chat session for document discussion
      const chatResponse = await fetch(`${API_BASE}/chat/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          title: `Discussion about ${documentTitle}`,
          message_type: 'document_analysis'
        })
      });

      if (chatResponse.ok) {
        const chatData = await chatResponse.json();
        
        // Send initial message about the document
        const messageResponse = await fetch(`${API_BASE}/chat/sessions/${chatData.id}/messages`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({
            message: `I want to discuss the document "${documentTitle}" (ID: ${documentId}). Please help me understand any risks or concerns I should be aware of.`,
            message_type: 'document_analysis'
          })
        });

        if (messageResponse.ok) {
          // Load the new chat session
          await loadChatSessions();
          // Open the new chat
          const newChat = await loadChatSession(chatData.id);
          if (newChat) {
            setSelectedChat(newChat);
          }
          setShowAnalysisModal(false);
        }
      }
    } catch (err) {
      console.error('Failed to add document to chat:', err);
    }
  };

  const getSafetyLevelColor = (level: string) => {
    switch (level) {
      case 'safe':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'dangerous':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'low':
        return 'text-green-600 bg-green-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'high':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text) return;
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setInput('');

    try {
      const token = localStorage.getItem('token');
      
      // Determine if this is a general legal question or document-specific query
      // If it mentions documents or specific legal documents, use RAG-based query
      // Otherwise, use direct Gemini API for general legal questions
      const isDocumentQuery = text.toLowerCase().includes('document') || 
                             text.toLowerCase().includes('uploaded') ||
                             recentDocuments.some(doc => text.toLowerCase().includes(doc.title.toLowerCase()));
      
      const endpoint = isDocumentQuery ? `${API_BASE}/query` : `${API_BASE}/gemini-query`;
      
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ question: text, top_k: 3 })
      });
      
      if (!res.ok) {
        const errTxt = await res.text();
        throw new Error(errTxt);
      }
      
      const data = await res.json();
      const sources = (data.sources || []) as Array<{ title: string; snippet: string }>;
      const sourcesBlock = sources.length
        ? `\n\nSources:\n${sources.map((s, i) => `${i + 1}. ${s.title} — ${s.snippet}`).join('\n')}`
        : '';
      
      setMessages((prev) => [
        ...prev,
        { role: 'ai', content: `${data.answer}${sourcesBlock}` },
      ]);
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        { role: 'ai', content: 'Sorry, there was an error contacting the assistant.' },
      ]);
    }
  };

  const handleKeyDown: React.KeyboardEventHandler<HTMLTextAreaElement> = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="flex flex-col md:flex-row h-screen antialiased relative">
      {/* Slide-out sidebar */}
      <aside className={`fixed md:relative z-30 h-full w-64 bg-[var(--card-background)] flex flex-col transform transition-transform duration-300 ease-in-out ${showSidebar ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div className="p-4 border-b border-[var(--border-color)]">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <svg className="h-6 w-6 text-[var(--primary-color)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M13 10V3L4 14h7v7l9-11h-7z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
            </svg>
            <Link to="/dashboard">LawGPT</Link>
          </h1>
        </div>
        <div className="flex-1 p-4 space-y-6 overflow-y-auto">
          <div className="space-y-2">
            <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">Actions</h2>
            <Link to="/dashboard" className="w-full flex items-center gap-3 p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
              </svg>
              <span className="text-sm">Home</span>
            </Link>
            <Link to="/upload" className="w-full flex items-center gap-3 p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 4v16m8-8H4" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
              </svg>
              <span className="text-sm">New Document</span>
            </Link>
            <Link to="/indian-legal-research" className="w-full flex items-center gap-3 p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
              </svg>
              <span className="text-sm">Indian Legal Research</span>
            </Link>
          </div>
          
          {/* Recent Chats Section */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">Recent Chats</h2>
              <button
                onClick={() => setShowNewChatModal(true)}
                className="text-xs text-[var(--primary-color)] hover:underline"
              >
                + New
              </button>
            </div>
            {loadingChats ? (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-[var(--primary-color)] mx-auto"></div>
                <p className="text-xs text-[var(--text-secondary)] mt-2">Loading chats...</p>
              </div>
            ) : recentChats.length === 0 ? (
              <div className="text-center py-4">
                <p className="text-xs text-[var(--text-secondary)]">No recent chats</p>
                <button
                  onClick={() => setShowNewChatModal(true)}
                  className="text-xs text-[var(--primary-color)] hover:underline"
                >
                  Start a new chat
                </button>
              </div>
            ) : (
              recentChats.map(chat => (
                <button
                  key={chat.id}
                  onClick={() => loadChatSession(chat.id)}
                  className={`w-full flex items-center gap-3 p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200 cursor-pointer ${
                    selectedChat?.id === chat.id ? 'bg-[var(--primary-color)]/10' : ''
                  }`}
                >
                  <svg className="h-5 w-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                  </svg>
                  <div className="flex-1 overflow-hidden text-left">
                    <p className="text-sm truncate">{chat.title}</p>
                    <p className="text-xs text-[var(--text-secondary)]">{chat.date}</p>
                  </div>
                </button>
              ))
            )}
          </div>
          
          {/* Recent Documents Section */}
          <div className="space-y-2">
            <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">Recent Documents</h2>
            {loadingDocuments ? (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-[var(--primary-color)] mx-auto"></div>
                <p className="text-xs text-[var(--text-secondary)] mt-2">Loading documents...</p>
              </div>
            ) : recentDocuments.length === 0 ? (
              <div className="text-center py-4">
                <p className="text-xs text-[var(--text-secondary)]">No documents uploaded yet</p>
                <Link to="/upload" className="text-xs text-[var(--primary-color)] hover:underline">
                  Upload your first document
                </Link>
              </div>
            ) : (
              recentDocuments.map(doc => (
                <div key={doc.id} className="w-full p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200">
                  <div className="flex items-center gap-3 mb-2">
                    <svg className="h-5 w-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                    </svg>
                    <div className="flex-1 overflow-hidden">
                      <p className="text-sm truncate">{doc.title}</p>
                      <p className="text-xs text-[var(--text-secondary)]">{doc.date}</p>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button
                      onClick={() => analyzeDocument(doc.id, doc.title)}
                      className="flex-1 text-xs bg-green-600 text-white px-2 py-1 rounded hover:bg-green-700 transition-colors duration-200"
                    >
                      Analyze
                    </button>
                    <button
                      onClick={() => addDocumentToChat(doc.id, doc.title)}
                      className="flex-1 text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700 transition-colors duration-200"
                    >
                      Add to Chat
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
          
          {/* Saved Analyses Section */}
          <div className="space-y-2">
            <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">Saved Analyses</h2>
            {loadingAnalyses ? (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-[var(--primary-color)] mx-auto"></div>
                <p className="text-xs text-[var(--text-secondary)] mt-2">Loading analyses...</p>
              </div>
            ) : savedAnalyses.length === 0 ? (
              <div className="text-center py-4">
                <p className="text-xs text-[var(--text-secondary)]">No analyses saved yet</p>
              </div>
            ) : (
              savedAnalyses.map(analysis => (
                <div key={analysis.id} className="w-full p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200">
                  <div className="flex items-center gap-3 mb-2">
                    <svg className="h-5 w-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                    </svg>
                    <div className="flex-1 overflow-hidden">
                      <p className="text-sm truncate">Analysis #{analysis.id}</p>
                      <p className="text-xs text-[var(--text-secondary)]">
                        {analysis.overall_risk_level.toUpperCase()} RISK • {new Date(analysis.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => loadSavedAnalysis(analysis.id)}
                    className="w-full text-xs bg-green-600 text-white px-2 py-1 rounded hover:bg-green-700 transition-colors duration-200"
                  >
                    View Analysis
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
        <div className="p-4 border-t border-[var(--border-color)] space-y-2">
          <Link to="/profile" className="w-full flex items-center gap-3 p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200">
            <div className="h-8 w-8 rounded-full bg-[var(--primary-color)] flex items-center justify-center">
              <span className="text-sm font-medium text-white">
                {userInfo ? userInfo.name.charAt(0).toUpperCase() : 'U'}
              </span>
            </div>
            <div className="flex-1 overflow-hidden">
              <span className="text-sm font-medium block truncate">
                {userInfo ? userInfo.name : 'User'}
              </span>
              <span className="text-xs text-[var(--text-secondary)] block truncate">
                {userInfo ? userInfo.email : 'user@example.com'}
              </span>
            </div>
          </Link>
          <button className="w-full flex items-center gap-3 p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200 text-red-400">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
            </svg>
            <span className="text-sm">Logout</span>
          </button>
        </div>
      </aside>
      
      {/* Overlay for mobile */}
      {showSidebar && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-20 md:hidden" 
          onClick={() => setShowSidebar(false)}
        ></div>
      )}
      <main className="flex-1 flex flex-col relative">  
        {/* Mobile header with menu button */}
        <div className="md:hidden flex items-center justify-between p-4 border-b border-[var(--border-color)]">
          <button 
            onClick={() => setShowSidebar(true)}
            className="p-2 rounded-md hover:bg-[var(--card-background)] transition-colors duration-200"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 6h16M4 12h16M4 18h16" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
            </svg>
          </button>
          <h1 className="text-xl font-bold flex items-center gap-2">
            <svg className="h-6 w-6 text-[var(--primary-color)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M13 10V3L4 14h7v7l9-11h-7z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
            </svg>
            <span>LawGPT</span>
          </h1>
          <div className="w-8"></div> {/* Empty div for balance */}
        </div>
        {selectedChat ? (
          /* Chat Interface */
          <div className="flex-1 flex flex-col">
            {/* Chat Header */}
            <div className="p-4 border-b border-[var(--border-color)] flex items-center justify-between">
              <div className="flex items-center gap-3">
                <button
                  onClick={closeChat}
                  className="p-2 rounded-md hover:bg-[var(--card-background)] transition-colors duration-200"
                >
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M15 19l-7-7 7-7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                  </svg>
                </button>
                <div>
                  <h2 className="text-lg font-semibold">{selectedChat.title}</h2>
                  <p className="text-sm text-[var(--text-secondary)]">
                    {selectedChat.messages.length} messages
                  </p>
                </div>
              </div>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 p-6 overflow-y-auto">
              {selectedChat.messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <div className="inline-block p-4 bg-[var(--card-background)] rounded-full mb-4">
                    <svg className="h-12 w-12 text-[var(--primary-color)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-[var(--primary-color)] mb-2">Start a conversation</h3>
                  <p className="text-[var(--text-secondary)] max-w-md">Ask me anything about legal matters. I can help with document analysis, legal research, and general legal questions.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {selectedChat.messages.map((message) => (
                    <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`${message.role === 'user' ? 'bg-[var(--primary-color)] text-[var(--background-color)]' : 'bg-[var(--card-background)]'} rounded-xl py-3 px-4 max-w-lg`}>
                        {message.role === 'assistant' && (
                          <p className="font-bold mb-1 text-[var(--primary-color)]">LegalAI</p>
                        )}
                        <p style={{ whiteSpace: 'pre-wrap' }}>{message.content}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {new Date(message.created_at).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  {loadingChat && (
                    <div className="flex justify-start">
                      <div className="bg-[var(--card-background)] rounded-xl py-3 px-4">
                        <div className="flex items-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-[var(--primary-color)]"></div>
                          <span className="text-sm text-[var(--text-secondary)]">Thinking...</span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>
              )}
            </div>

            {/* Chat Input */}
            <div className="p-6 border-t border-[var(--border-color)]">
              <div className="relative">
                <textarea
                  className="w-full bg-[var(--card-background)] border border-[var(--border-color)] rounded-xl resize-none py-3 pr-20 pl-4 focus:outline-none focus:ring-2 focus:ring-[var(--primary-color)] focus:border-transparent transition-all duration-200"
                  placeholder="Type your message here..."
                  rows={1}
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={handleChatKeyDown}
                  disabled={loadingChat}
                />
                <button
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-[var(--primary-color)] text-[var(--background-color)] hover:bg-[var(--accent-color)] transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={sendChatMessage}
                  disabled={!chatInput.trim() || loadingChat}
                >
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* Default Dashboard Content */
          <>
            {!hasMessages && (
              <div className="flex-1 p-6 flex flex-col justify-center items-center">
                <div className="text-center">
                  <div className="inline-block p-4 bg-[var(--card-background)] rounded-full mb-4">
                    <svg className="h-12 w-12 text-[var(--primary-color)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5"></path>
                      <path d="M12 18a.96.96 0 00.96-.96v-.08a.96.96 0 00-.96-.96.96.96 0 00-.96.96v.08c0 .53.43.96.96.96zM12 6.5c-1.66 0-3 1.34-3 3v.5h1.5v-.5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5S12.83 13 12 13s-1.5-.67-1.5-1.5H9v.5c0 2.48 2.02 4.5 4.5 4.5s4.5-2.02 4.5-4.5z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5"></path>
                    </svg>
                  </div>
                  <h2 className="text-3xl font-bold text-[var(--primary-color)] mb-2">How can I help you today?</h2>
                  <p className="text-[var(--text-secondary)] max-w-md mx-auto">Ask me anything about legal matters. Please note I am an AI assistant and not a substitute for a human lawyer.</p>
                </div>
              </div>
            )}
            {hasMessages && (
              <div className="chat-container flex-1 p-6 overflow-y-auto" ref={historyRef}>
                {messages.map((m, idx) => (
                  <div key={idx} className={`flex mb-4 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`${m.role === 'user' ? 'bg-[var(--primary-color)] text-[var(--background-color)]' : 'bg-[var(--card-background)]'} rounded-xl py-2 px-4 max-w-lg`}>
                      {m.role === 'ai' && <p className="font-bold mb-1 text-[var(--primary-color)]">LegalAI</p>}
                      <p style={{ whiteSpace: 'pre-wrap' }}>{m.content}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
        {!selectedChat && (
          <div className="p-6 border-t border-[var(--border-color)]">
            <div className="relative">
              <textarea
                className="w-full bg-[var(--card-background)] border border-[var(--border-color)] rounded-xl resize-none py-3 pr-20 pl-4 focus:outline-none focus:ring-2 focus:ring-[var(--primary-color)] focus:border-transparent transition-all duration-200"
                placeholder="Ask your legal question here..."
                rows={1}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
              />
              <button
                className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-[var(--primary-color)] text-[var(--background-color)] hover:bg-[var(--accent-color)] transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={sendMessage}
                disabled={!input.trim()}
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 10l7-7m0 0l7 7m-7-7v18" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                </svg>
              </button>
            </div>
            <p className="text-xs text-center text-[var(--text-secondary)] mt-2">LawGPT can make mistakes. Consider checking important information.</p>
          </div>
        )}
      </main>

      {/* New Chat Modal */}
      {showNewChatModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-[var(--card-background)] rounded-xl p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">Create New Chat</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                  Chat Title
                </label>
                <input
                  type="text"
                  value={newChatTitle}
                  onChange={(e) => setNewChatTitle(e.target.value)}
                  placeholder="Enter chat title..."
                  className="w-full bg-[var(--background-color)] border border-[var(--border-color)] rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--primary-color)] focus:border-transparent"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      createNewChat();
                    }
                  }}
                />
              </div>
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => {
                    setShowNewChatModal(false);
                    setNewChatTitle('');
                  }}
                  className="px-4 py-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors duration-200"
                >
                  Cancel
                </button>
                <button
                  onClick={createNewChat}
                  disabled={!newChatTitle.trim()}
                  className="px-4 py-2 bg-[var(--primary-color)] text-white rounded-lg hover:bg-[var(--accent-color)] transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Create Chat
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Document Analysis Modal */}
      {showAnalysisModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-[var(--card-background)] rounded-xl w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="p-6 border-b border-[var(--border-color)] flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold text-[var(--text-primary)]">Document Analysis</h3>
                <p className="text-[var(--text-secondary)]">{selectedDocument?.title}</p>
              </div>
              <button
                onClick={() => setShowAnalysisModal(false)}
                className="p-2 rounded-lg hover:bg-[var(--secondary-color)]/20 transition-colors duration-200"
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M6 18L18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                </svg>
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {analyzingDocument ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
                  <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-2">Analyzing Document...</h2>
                  <p className="text-[var(--text-secondary)]">This may take a few moments</p>
                </div>
              ) : analysisError ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <div className="text-red-500 text-4xl mb-4">⚠️</div>
                  <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-2">Analysis Failed</h2>
                  <p className="text-[var(--text-secondary)] mb-4">{analysisError}</p>
                  <button
                    onClick={() => setShowAnalysisModal(false)}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    Close
                  </button>
                </div>
              ) : documentAnalysis ? (
                <div className="space-y-6">
                  {/* Summary Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div className="flex items-center">
                        <div className="p-2 bg-green-100 rounded-lg">
                          <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-green-600">Total Clauses</p>
                          <p className="text-2xl font-semibold text-green-800">{documentAnalysis.total_clauses}</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div className="flex items-center">
                        <div className="p-2 bg-green-100 rounded-lg">
                          <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-green-600">Safe Clauses</p>
                          <p className="text-2xl font-semibold text-green-800">{documentAnalysis.safe_clauses}</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <div className="flex items-center">
                        <div className="p-2 bg-yellow-100 rounded-lg">
                          <svg className="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                          </svg>
                        </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-yellow-600">Warning Clauses</p>
                          <p className="text-2xl font-semibold text-yellow-800">{documentAnalysis.warning_clauses}</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <div className="flex items-center">
                        <div className="p-2 bg-red-100 rounded-lg">
                          <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-red-600">Dangerous Clauses</p>
                          <p className="text-2xl font-semibold text-red-800">{documentAnalysis.dangerous_clauses}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Overall Risk Assessment */}
                  <div className="bg-[var(--card-background)] border border-[var(--border-color)] rounded-lg p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-[var(--text-primary)]">Overall Risk Assessment</h3>
                        <p className="text-[var(--text-secondary)]">Based on the analysis of all clauses</p>
                      </div>
                      <div className={`px-4 py-2 rounded-full text-sm font-medium ${getRiskLevelColor(documentAnalysis.overall_risk_level)}`}>
                        {documentAnalysis.overall_risk_level.toUpperCase()} RISK
                      </div>
                    </div>
                  </div>

                  {/* Analysis Summary */}
                  <div className="bg-[var(--card-background)] border border-[var(--border-color)] rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Analysis Summary</h3>
                    <div className="prose max-w-none">
                      <pre className="whitespace-pre-wrap text-sm text-[var(--text-secondary)]">{documentAnalysis.summary}</pre>
                    </div>
                  </div>

                  {/* Detailed Clause Analysis */}
                  <div className="bg-[var(--card-background)] border border-[var(--border-color)] rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Detailed Clause Analysis</h3>
                    <div className="space-y-4">
                      {documentAnalysis.clauses.map((clause: any, index: number) => (
                        <div
                          key={index}
                          className={`border rounded-lg p-4 ${getSafetyLevelColor(clause.safety_level)}`}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              <span className="px-2 py-1 text-xs font-medium rounded-full bg-white">
                                {clause.clause_type.replace('_', ' ')}
                              </span>
                              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                clause.safety_level === 'safe' ? 'bg-green-200 text-green-800' :
                                clause.safety_level === 'warning' ? 'bg-yellow-200 text-yellow-800' :
                                'bg-red-200 text-red-800'
                              }`}>
                                {clause.safety_level.toUpperCase()}
                              </span>
                            </div>
                          </div>
                          
                          <div className="mb-3">
                            <p className="text-sm font-medium text-[var(--text-primary)] mb-1">Clause Text:</p>
                            <p className="text-sm text-[var(--text-secondary)] bg-white p-3 rounded border">
                              {clause.clause_text}
                            </p>
                          </div>
                          
                          <div className="mb-3">
                            <p className="text-sm font-medium text-[var(--text-primary)] mb-1">Analysis:</p>
                            <p className="text-sm text-[var(--text-secondary)]">{clause.explanation}</p>
                          </div>
                          
                          {clause.recommendations && (
                            <div>
                              <p className="text-sm font-medium text-[var(--text-primary)] mb-1">Recommendations:</p>
                              <p className="text-sm text-[var(--text-secondary)] bg-green-50 p-3 rounded border">
                                {clause.recommendations}
                              </p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-4 justify-center">
                    <button
                      onClick={() => selectedDocument && addDocumentToChat(selectedDocument.id, selectedDocument.title)}
                      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center gap-2"
                    >
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                      </svg>
                      Add to Chat for Discussion
                    </button>
                    <button
                      onClick={() => setShowAnalysisModal(false)}
                      className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200"
                    >
                      Close Analysis
                    </button>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;


