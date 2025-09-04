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
  const [recentDocuments, setRecentDocuments] = useState([
    { id: 1, title: 'Contract Agreement', date: '2023-05-15' },
    { id: 2, title: 'Legal Brief', date: '2023-05-10' },
    { id: 3, title: 'Case Study', date: '2023-05-05' },
  ]);
  
  // Close sidebar when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (showSidebar && !target.closest('.sidebar') && !target.closest('.menu-button')) {
        setShowSidebar(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSidebar]);

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

      setSuccess(true);
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (err: any) {
      setError('Upload failed: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="dark">
      <div className="relative flex size-full min-h-screen flex-col bg-[var(--background-color)] overflow-x-hidden">
        {/* Mobile Header */}
        <header className="md:hidden flex items-center justify-between whitespace-nowrap border-b border-solid border-gray-700 px-4 py-4">
          <button 
            className="menu-button flex items-center justify-center rounded-full h-10 w-10 bg-gray-800 text-[var(--text-secondary)] hover:bg-gray-700 hover:text-[var(--text-primary)] transition-colors"
            onClick={() => setShowSidebar(!showSidebar)}
          >
            <svg fill="none" height="24" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
              <line x1="4" x2="20" y1="12" y2="12"></line>
              <line x1="4" x2="20" y1="6" y2="6"></line>
              <line x1="4" x2="20" y1="18" y2="18"></line>
            </svg>
          </button>
          <div className="flex items-center gap-4 text-[var(--text-primary)]">
            <div className="size-6 text-[var(--primary-color)]">
              <svg fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                <path d="M2 7L12 12L22 7" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                <path d="M12 22V12" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
              </svg>
            </div>
            <Link to="/dashboard" className="text-xl font-bold tracking-tight">LawGPT</Link>
          </div>
          <Link to="/profile" className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10" style={{ backgroundImage: 'url(https://lh3.googleusercontent.com/aida-public/AB6AXuDIZ91X9HWSiwKrwB-iywUliq4fSq5LH_TdTTeHCdZfzZDW-uCSeq-60zM21TzAZHqBEGwZTw8UEz37k709OSThA_acmbSDQA19SoB_7akprqU6aD5r4XooCATjixK4fuFbxvRGSllkYpiORuiTHi7C4jePM7HOdW5FCfU8M2J2gt8lbOnKpcx4EsLQpD2yJWrI49mK690caY9fexd5e8_9IJKXg54H-817Ff83X10mcro17YTF0m-QW0MK2Ad70XqwsGRVk88DydQU)' }} />
        </header>
        
        <div className="layout-container flex h-full grow flex-col">
          {/* Desktop Header */}
          <header className="hidden md:flex items-center justify-between whitespace-nowrap border-b border-solid border-gray-700 px-10 py-4">
            <div className="flex items-center gap-4 text-[var(--text-primary)]">
              <div className="size-6 text-[var(--primary-color)]">
                <svg fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                  <path d="M2 7L12 12L22 7" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                  <path d="M12 22V12" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                </svg>
              </div>
              <Link to="/dashboard" className="text-xl font-bold tracking-tight">LawGPT</Link>
            </div>
            <nav className="hidden md:flex items-center gap-8">
              <Link to="/dashboard" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">Home</Link>
              <Link to="/upload" className="text-sm font-medium text-[var(--text-primary)]">Documents</Link>
              <Link to="/dashboard" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">Chat</Link>
            </nav>
            <div className="flex items-center gap-4">
              <button 
                className="menu-button flex items-center justify-center rounded-full h-10 w-10 bg-gray-800 text-[var(--text-secondary)] hover:bg-gray-700 hover:text-[var(--text-primary)] transition-colors"
                onClick={() => setShowSidebar(!showSidebar)}
              >
                <svg fill="none" height="24" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                  <rect height="14" rx="2" ry="2" width="20" x="2" y="7"></rect>
                  <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                </svg>
              </button>
              <Link to="/profile" className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10" style={{ backgroundImage: 'url(https://lh3.googleusercontent.com/aida-public/AB6AXuDIZ91X9HWSiwKrwB-iywUliq4fSq5LH_TdTTeHCdZfzZDW-uCSeq-60zM21TzAZHqBEGwZTw8UEz37k709OSThA_acmbSDQA19SoB_7akprqU6aD5r4XooCATjixK4fuFbxvRGSllkYpiORuiTHi7C4jePM7HOdW5FCfU8M2J2gt8lbOnKpcx4EsLQpD2yJWrI49mK690caY9fexd5e8_9IJKXg54H-817Ff83X10mcro17YTF0m-QW0MK2Ad70XqwsGRVk88DydQU)' }} />
            </div>
          </header>
          
          {/* Sliding Sidebar */}
          <aside className={`sidebar fixed top-0 left-0 z-40 h-screen w-64 bg-gray-900 border-r border-gray-700 transform transition-transform duration-300 ease-in-out ${showSidebar ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 md:static md:h-auto md:w-64`}>
            <div className="flex flex-col h-full p-4">
              <div className="flex items-center gap-4 mb-8 p-2">
                <div className="size-8 text-[var(--primary-color)]">
                  <svg fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                    <path d="M2 7L12 12L22 7" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                    <path d="M12 22V12" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                  </svg>
                </div>
                <span className="text-xl font-bold text-white">LawGPT</span>
              </div>
              
              <nav className="flex flex-col gap-2">
                <Link to="/dashboard" className="flex items-center gap-3 rounded-lg px-3 py-2 text-[var(--text-secondary)] transition-colors hover:bg-gray-800 hover:text-white">
                  <svg className="size-5" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                  </svg>
                  <span>Home</span>
                </Link>
                <Link to="/upload" className="flex items-center gap-3 rounded-lg px-3 py-2 bg-gray-800 text-white transition-colors">
                  <svg className="size-5" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="12" y1="18" x2="12" y2="12"></line>
                    <line x1="9" y1="15" x2="15" y2="15"></line>
                  </svg>
                  <span>Documents</span>
                </Link>
                <Link to="/profile" className="flex items-center gap-3 rounded-lg px-3 py-2 text-[var(--text-secondary)] transition-colors hover:bg-gray-800 hover:text-white">
                  <svg className="size-5" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                  <span>Profile</span>
                </Link>
              </nav>
              
              <div className="mt-4 border-t border-gray-700 pt-4">
                <h3 className="mb-2 px-3 text-xs font-medium uppercase text-gray-500">Recent Documents</h3>
                <div className="space-y-1">
                  {recentDocuments.map(doc => (
                    <a key={doc.id} href="#" className="flex items-center gap-3 rounded-lg px-3 py-2 text-[var(--text-secondary)] transition-colors hover:bg-gray-800 hover:text-white">
                      <svg className="size-4" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                      </svg>
                      <span className="truncate">{doc.title}</span>
                    </a>
                  ))}
                </div>
              </div>
              
              <div className="mt-auto">
                <button 
                  onClick={() => {
                    localStorage.removeItem('token');
                    navigate('/');
                  }}
                  className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-red-400 transition-colors hover:bg-red-500/10"
                >
                  <svg className="size-5" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                    <polyline points="16 17 21 12 16 7"></polyline>
                    <line x1="21" y1="12" x2="9" y2="12"></line>
                  </svg>
                  <span>Logout</span>
                </button>
              </div>
            </div>
          </aside>
          
          <main className="flex flex-1 justify-center py-12 px-4 sm:px-6 lg:px-8 md:ml-64">
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
                      className={`bg-gray-800/50 border-2 border-dashed ${file ? 'border-[var(--primary-color)]' : 'border-gray-600'} rounded-2xl p-8 text-center transition-all hover:border-[var(--primary-color)] hover:bg-gray-800`}
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
                        <label className="relative cursor-pointer rounded-full bg-[var(--primary-color)] text-black px-6 py-3 font-semibold hover:bg-[var(--accent-color)] focus-within:outline-none focus-within:ring-2 focus-within:ring-[var(--primary-color)] focus-within:ring-opacity-50 focus-within:ring-offset-2 focus-within:ring-offset-background-color transition-colors">
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
                        className="w-full p-3 bg-[var(--input-bg-color)] border border-[var(--border-color)] rounded-lg text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:border-[var(--primary-color)] focus:ring-1 focus:ring-[var(--primary-color)] transition-colors"
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
                        className="w-full inline-flex justify-center items-center bg-[var(--primary-color)] text-black py-3 px-6 rounded-lg font-bold hover:bg-[var(--accent-color)] transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-[var(--primary-color)] focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={loading || !file}
                      >
                        {loading ? (
                          <>
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
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
          </main>
        </div>
      </div>
    </div>
  );
};

export default UploadDoc;


