import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const API_BASE = '/api';

const UploadDoc: React.FC = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const [recentDocuments, setRecentDocuments] = useState<Array<{ id: number; title: string; date: string; content_type: string }>>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(false);
  const [userInfo, setUserInfo] = useState<{ name: string; email: string } | null>(null);
  
  useEffect(() => {
    loadDocuments();
    loadUserInfo();
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      if (!title) {
        // Use filename as default title
        setTitle(e.target.files[0].name.split('.')[0]);
      }
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      if (!title) {
        // Use filename as default title
        setTitle(e.dataTransfer.files[0].name.split('.')[0]);
      }
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file to upload');
      return;
    }
    if (!title.trim()) {
      setError('Please enter a title for your document');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('You must be logged in to upload documents');
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title);

      const res = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData
      });

      if (!res.ok) {
        throw new Error(await res.text());
      }

      const result = await res.json();
      setSuccess(true);
      
      // Refresh documents list
      loadDocuments();
      
      // Show analysis option
      if (window.confirm('Document uploaded successfully! Would you like to analyze it for legal clauses and safety assessment?')) {
        navigate(`/document-analysis/${result.document_id}`);
      } else {
        setTimeout(() => {
          navigate('/dashboard');
        }, 2000);
      }
    } catch (err: any) {
      setError('Upload failed: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };
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
            <Link to="/upload" className="w-full flex items-center gap-3 p-2 rounded-md bg-[var(--primary-color)]/10 text-[var(--primary-color)] transition-colors duration-200">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 4v16m8-8H4" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
              </svg>
              <span className="text-sm">New Document</span>
            </Link>
            <Link to="/chat" className="w-full flex items-center gap-3 p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
              </svg>
              <span className="text-sm">Legal Chat</span>
            </Link>
            <Link to="/indian-legal-research" className="w-full flex items-center gap-3 p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
              </svg>
              <span className="text-sm">Indian Legal Research</span>
            </Link>
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
              </div>
            ) : (
              recentDocuments.map(doc => (
                <div key={doc.id} className="w-full p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200">
                  <div className="flex items-center gap-3">
                    <svg className="h-5 w-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                    </svg>
                    <div className="flex-1 overflow-hidden">
                      <p className="text-sm truncate">{doc.title}</p>
                      <p className="text-xs text-[var(--text-secondary)]">{doc.date}</p>
                    </div>
                  </div>
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
          <button 
            onClick={() => {
              localStorage.removeItem('token');
              navigate('/');
            }}
            className="w-full flex items-center gap-3 p-2 rounded-md hover:bg-[var(--secondary-color)]/20 transition-colors duration-200 text-red-400"
          >
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

        {/* Main Content */}
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="w-full max-w-3xl space-y-8">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-[var(--text-primary)] mb-2">Upload Your Documents</h1>
              <p className="text-lg text-[var(--text-secondary)]">Upload legal documents to LawGPT for analysis. Accepted file types: PDF, DOCX, TXT.</p>
            </div>
            
            <form onSubmit={handleSubmit}>
              {success ? (
                <div className="bg-green-900/30 border border-green-700 rounded-2xl p-8 text-center">
                  <div className="flex flex-col items-center justify-center space-y-4">
                    <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-500/20 text-green-500">
                      <svg className="h-8 w-8" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round"></path>
                      </svg>
                    </div>
                    <p className="text-xl font-semibold text-[var(--text-primary)]">Document uploaded successfully!</p>
                    <p className="text-sm text-[var(--text-secondary)]">Redirecting to dashboard...</p>
                  </div>
                </div>
              ) : (
                <>
                  <div 
                    className={`bg-[var(--card-background)] border-2 border-dashed ${file ? 'border-[var(--primary-color)]' : 'border-[var(--border-color)]'} rounded-2xl p-8 text-center transition-all hover:border-[var(--primary-color)] hover:bg-[var(--secondary-color)]/10`}
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                  >
                    <div className="flex flex-col items-center justify-center space-y-6">
                      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[var(--primary-color)]/20 text-[var(--primary-color)]">
                        <svg className="h-8 w-8" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M7 16a4 4 0 01-4-4V6a4 4 0 014-4h4a4 4 0 014 4v6m-4-6h.01M7 16h.01M7 16l4-4m-4 4l-4-4m12 4h.01M17 16h.01M17 16l-4-4m4 4l4-4m-6-4v12m0 0l-4-4m4 4l4-4" strokeLinecap="round" strokeLinejoin="round"></path>
                        </svg>
                      </div>
                      {file ? (
                        <div className="space-y-2">
                          <p className="text-xl font-semibold text-[var(--text-primary)]">{file.name}</p>
                          <p className="text-sm text-[var(--text-secondary)]">{(file.size / 1024).toFixed(2)} KB</p>
                        </div>
                      ) : (
                        <div className="space-y-2">
                          <p className="text-xl font-semibold text-[var(--text-primary)]">Drag and drop files here</p>
                          <p className="text-sm text-[var(--text-secondary)]">or</p>
                        </div>
                      )}
                      <label className="relative cursor-pointer rounded-full bg-[var(--primary-color)] text-white px-6 py-3 font-semibold hover:bg-[var(--accent-color)] focus-within:outline-none focus-within:ring-2 focus-within:ring-[var(--primary-color)] focus-within:ring-opacity-50 focus-within:ring-offset-2 focus-within:ring-offset-background-color transition-colors">
                        <span>{file ? 'Change File' : 'Browse Files'}</span>
                        <input className="sr-only" id="file-upload" name="file-upload" type="file" onChange={handleFileChange} />
                      </label>
                    </div>
                  </div>
                  
                  <div className="mt-6">
                    <label className="block text-sm font-medium text-[var(--text-primary)] mb-2" htmlFor="title">Document Title</label>
                    <input 
                      type="text" 
                      id="title" 
                      className="w-full p-3 bg-[var(--card-background)] border border-[var(--border-color)] rounded-lg text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:border-[var(--primary-color)] focus:ring-1 focus:ring-[var(--primary-color)] transition-colors"
                      placeholder="Enter document title"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      required
                    />
                  </div>
                  
                  {error && (
                    <div className="mt-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-400 text-sm">
                      {error}
                    </div>
                  )}
                  
                  <div className="mt-6">
                    <button 
                      type="submit" 
                      className="w-full inline-flex justify-center items-center bg-[var(--primary-color)] text-white py-3 px-6 rounded-lg font-bold hover:bg-[var(--accent-color)] transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-[var(--primary-color)] focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      disabled={loading || !file}
                    >
                      {loading ? (
                        <>
                          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Uploading...
                        </>
                      ) : 'Upload Document'}
                    </button>
                  </div>
                </>
              )}
            </form>
          </div>
        </div>
      </main>
    </div>
  );
};

export default UploadDoc;


