import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';

const API_BASE = '/api';

const Dashboard: React.FC = () => {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'ai'; content: string }>>([]);
  const [input, setInput] = useState('');
  const [showSidebar, setShowSidebar] = useState(false);
  const historyRef = useRef<HTMLDivElement | null>(null);
  const [recentDocuments, setRecentDocuments] = useState([
    { id: 1, title: 'Employment Policy', date: '2023-10-15' },
    { id: 2, title: 'NDA Agreement', date: '2023-10-10' },
    { id: 3, title: 'Services Agreement', date: '2023-09-28' },
  ]);
  const [recentChats, setRecentChats] = useState([
    { id: 1, title: 'Employment Law Question', date: '2023-10-18' },
    { id: 2, title: 'Contract Review', date: '2023-10-12' },
    { id: 3, title: 'Intellectual Property Rights', date: '2023-10-05' },
  ]);

  useEffect(() => {
    if (historyRef.current) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight;
    }
  }, [messages]);

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
          </div>
          
          {/* Recent Chats Section */}
          <div className="space-y-2">
            <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">Recent Chats</h2>
            {recentChats.map(chat => (
              <div key={chat.id} className="w-full flex items-center gap-3 p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200 cursor-pointer">
                <svg className="h-5 w-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                </svg>
                <div className="flex-1 overflow-hidden">
                  <p className="text-sm truncate">{chat.title}</p>
                  <p className="text-xs text-[var(--text-secondary)]">{chat.date}</p>
                </div>
              </div>
            ))}
          </div>
          
          {/* Recent Documents Section */}
          <div className="space-y-2">
            <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">Recent Documents</h2>
            {recentDocuments.map(doc => (
              <div key={doc.id} className="w-full flex items-center gap-3 p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200 cursor-pointer">
                <svg className="h-5 w-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                </svg>
                <div className="flex-1 overflow-hidden">
                  <p className="text-sm truncate">{doc.title}</p>
                  <p className="text-xs text-[var(--text-secondary)]">{doc.date}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="p-4 border-t border-[var(--border-color)] space-y-2">
          <Link to="/profile" className="w-full flex items-center gap-3 p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200">
            <img alt="User Avatar" className="h-8 w-8 rounded-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuD4IH31bIsF4hMGofg3pe6t7pd--2yLHZu_-lPS6cDKyY3SkKqgdK3lIqsXw6WdeOkjk4Z8yNzFrPFQf-qnfQO9HIlvttGAZEVTf8lH_xdLTA_FX6uYkuC18RZXDYfMnYx6v36jBwHDNa7svnKCXE98kbRy9ttdyP7FVrvRxoxhsPwmSOfNQsDJAj8eHNBsNg0DtNFNKJzsVqycU_r78nnFM8zgXtlk6w0nxxMMKwfwFUZ0RR5B5H_nmpaUV1pWC_NoGrXsG3aEOoSr" />
            <span className="text-sm font-medium">John Doe</span>
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
      </main>
    </div>
  );
};

export default Dashboard;


