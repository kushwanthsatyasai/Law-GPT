import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config/api';

// Define API base URL
const API_BASE = API_BASE_URL;

const Profile: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<{username: string, email: string} | null>(null);
  const [recentDocuments, setRecentDocuments] = useState<{id: string, title: string, date: string}[]>([]);
  const [recentQueries, setRecentQueries] = useState<{id: string, question: string, date: string}[]>([]);
  const [showSidebar, setShowSidebar] = useState(false);
  
  useEffect(() => {
    // Fetch user profile data
    const fetchUserProfile = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/');
          return;
        }
        
        // Mock data for now - in a real app, you would fetch this from the backend
        setUser({
          username: 'John Doe',
          email: 'john.doe@example.com'
        });
        
        setRecentDocuments([
          { id: '1', title: 'Contract Agreement.pdf', date: '2023-06-15' },
          { id: '2', title: 'Legal Brief.pdf', date: '2023-06-10' },
          { id: '3', title: 'Case Study.pdf', date: '2023-06-05' }
        ]);
        
        setRecentQueries([
          { id: '1', question: 'What are my rights as a tenant?', date: '2023-06-15' },
          { id: '2', question: 'How do I file for bankruptcy?', date: '2023-06-10' },
          { id: '3', question: 'What is the process for a divorce?', date: '2023-06-05' }
        ]);
      } catch (err) {
        setError('Failed to load profile data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUserProfile();
  }, [navigate]);
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };
  
  const toggleSidebar = () => {
    setShowSidebar(!showSidebar);
  };
  return (
    <div className="bg-[var(--background-color)] text-[var(--text-primary)] min-h-screen">
      <div className="relative flex size-full min-h-screen flex-col overflow-x-hidden">
        {/* Mobile Header */}
        <header className="md:hidden flex items-center justify-between p-4 bg-gray-800">
          <div className="flex items-center gap-2">
            <svg className="text-[var(--primary-color)]" fill="none" height="28" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="28" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
            <span className="text-xl font-bold text-white">LawGPT</span>
          </div>
          <button onClick={toggleSidebar} className="text-white">
            <svg fill="none" height="24" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="24">
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>
        </header>
        
        <div className="flex h-full grow flex-col">
          <div className="flex flex-1">
            {/* Sidebar - with slide functionality for mobile */}
            <aside className={`${showSidebar ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 fixed md:relative z-10 flex w-64 flex-col bg-gray-900 p-4 h-full transition-transform duration-300 ease-in-out`}>
              <div className="mb-8 flex items-center gap-2">
                <svg className="text-[var(--primary-color)]" fill="none" height="28" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="28" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
                <Link to="/dashboard" className="text-xl font-bold text-white">LawGPT</Link>
              </div>
              <nav className="flex flex-col gap-2">
                <Link className="flex items-center gap-3 rounded-md px-3 py-2 text-[var(--text-secondary)] transition-colors hover:bg-[var(--secondary-color)]" to="/dashboard">
                  <svg fill="none" height="24" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                    <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                  </svg>
                  <span>Home</span>
                </Link>
                <a className="flex items-center gap-3 rounded-md px-3 py-2 text-[var(--text-secondary)] transition-colors hover:bg-[var(--secondary-color)]" href="#">
                  <svg fill="none" height="24" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                  </svg>
                  <span>Chat</span>
                </a>
                <a className="flex items-center gap-3 rounded-md px-3 py-2 text-[var(--text-secondary)] transition-colors hover:bg-[var(--secondary-color)]" href="#">
                  <svg fill="none" height="24" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                  </svg>
                  <span>Documents</span>
                </a>
                <a className="flex items-center gap-3 rounded-md px-3 py-2 text-[var(--text-secondary)] transition-colors hover:bg-[var(--secondary-color)]" href="#">
                  <svg fill="none" height="24" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                  <span>Profile</span>
                </a>
                <a className="flex items-center gap-3 rounded-md bg-[var(--secondary-color)] px-3 py-2 text-white transition-colors" href="#">
                  <svg fill="none" height="24" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 0 2l-.15.08a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1 0-2l.15-.08a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                  <span>Settings</span>
                </a>
              </nav>
              <div className="mt-auto flex flex-col gap-2">
                <button onClick={handleLogout} className="flex items-center gap-3 rounded-md px-3 py-2 text-[var(--text-secondary)] transition-colors hover:bg-[var(--secondary-color)]">
                  <svg fill="none" height="24" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                    <polyline points="16 17 21 12 16 7"></polyline>
                    <line x1="21" y1="12" x2="9" y2="12"></line>
                  </svg>
                  <span>Logout</span>
                </button>
              </div>
            </aside>
            <main className="flex-1 p-8 md:ml-64">
              {loading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[var(--primary-color)]"></div>
                </div>
              ) : error ? (
                <div className="text-red-500 text-center">{error}</div>
              ) : (
                <>
                  <header className="mb-8 flex items-center justify-between">
                    <h1 className="text-3xl font-bold text-white">Profile</h1>
                  </header>
                  
                  {/* User Profile Card */}
                  <div className="mb-8 bg-gray-800 rounded-lg p-6">
                    <div className="flex flex-col md:flex-row items-center gap-6">
                      <div className="flex-shrink-0">
                        <div className="w-24 h-24 rounded-full bg-[var(--secondary-color)] flex items-center justify-center text-white text-3xl font-bold">
                          {user?.username.charAt(0)}
                        </div>
                      </div>
                      <div className="flex-grow text-center md:text-left">
                        <h2 className="text-2xl font-bold text-white">{user?.username}</h2>
                        <p className="text-[var(--text-secondary)]">{user?.email}</p>
                        <div className="mt-4 flex flex-wrap gap-2 justify-center md:justify-start">
                          <button className="px-4 py-2 bg-[var(--primary-color)] text-white rounded-md hover:bg-opacity-80 transition-colors">
                            Edit Profile
                          </button>
                          <button className="px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-opacity-80 transition-colors">
                            Change Password
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Recent Documents */}
                    <div className="bg-gray-800 rounded-lg p-6">
                      <h2 className="text-xl font-semibold text-white mb-4">Recent Documents</h2>
                      {recentDocuments.length > 0 ? (
                        <div className="space-y-4">
                          {recentDocuments.map(doc => (
                            <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-700 rounded-md hover:bg-gray-600 transition-colors">
                              <div className="flex items-center gap-3">
                                <svg className="text-[var(--primary-color)]" fill="none" height="20" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="20">
                                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                  <polyline points="14 2 14 8 20 8"></polyline>
                                </svg>
                                <span className="text-white">{doc.title}</span>
                              </div>
                              <span className="text-sm text-[var(--text-secondary)]">{doc.date}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-[var(--text-secondary)]">No documents uploaded yet.</p>
                      )}
                      <div className="mt-4">
                        <Link to="/upload" className="text-[var(--primary-color)] hover:underline">Upload new document</Link>
                      </div>
                    </div>
                    
                    {/* Recent Queries */}
                    <div className="bg-gray-800 rounded-lg p-6">
                      <h2 className="text-xl font-semibold text-white mb-4">Recent Queries</h2>
                      {recentQueries.length > 0 ? (
                        <div className="space-y-4">
                          {recentQueries.map(query => (
                            <div key={query.id} className="p-3 bg-gray-700 rounded-md hover:bg-gray-600 transition-colors">
                              <div className="flex items-center gap-3 mb-2">
                                <svg className="text-[var(--primary-color)]" fill="none" height="20" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="20">
                                  <circle cx="12" cy="12" r="10"></circle>
                                  <line x1="12" y1="16" x2="12" y2="12"></line>
                                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                                </svg>
                                <span className="text-white font-medium">Question</span>
                              </div>
                              <p className="text-[var(--text-secondary)] ml-7">{query.question}</p>
                              <div className="mt-2 text-right">
                                <span className="text-sm text-[var(--text-secondary)]">{query.date}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-[var(--text-secondary)]">No queries yet.</p>
                      )}
                      <div className="mt-4">
                        <Link to="/dashboard" className="text-[var(--primary-color)] hover:underline">Ask a new question</Link>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </main>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;


