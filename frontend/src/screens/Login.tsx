import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const API_BASE = '/api';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Login failed');
      }
      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      
      // Store user email for immediate use
      localStorage.setItem('userEmail', email);
      localStorage.setItem('userName', email.split('@')[0].replace(/^\w/, c => c.toUpperCase()));
      
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="dark">
      <div className="relative flex size-full min-h-screen flex-col bg-[var(--background-color)] overflow-x-hidden">
        <div className="flex h-full grow flex-col">
          <header className="flex items-center justify-between whitespace-nowrap px-10 py-4 border-b border-gray-800">
            <div className="flex items-center gap-4 text-[var(--text-primary)]">
              <svg className="h-8 w-8 text-[var(--primary-color)]" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 18.375a3.375 3.375 0 0 0 3.375-3.375h-6.75A3.375 3.375 0 0 0 12 18.375ZM12 5.625A3.375 3.375 0 0 1 15.375 9H8.625A3.375 3.375 0 0 1 12 5.625ZM3.375 9a8.625 8.625 0 0 1 17.25 0v6.75a8.625 8.625 0 0 1-17.25 0V9Z" strokeLinecap="round" strokeLinejoin="round"></path>
              </svg>
              <Link to="/dashboard" className="text-2xl font-bold tracking-tight">LawGPT</Link>
            </div>
            <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-[var(--text-secondary)]">
              <a className="hover:text-[var(--text-primary)] transition-colors" href="#">Home</a>
              <a className="hover:text-[var(--text-primary)] transition-colors" href="#">About</a>
              <a className="hover:text-[var(--text-primary)] transition-colors" href="#">Contact</a>
            </nav>
          </header>
          <main className="flex flex-1 items-center justify-center p-4 sm:p-6 md:p-8">
            <div className="w-full max-w-md space-y-8 rounded-2xl bg-gray-900/50 p-8 shadow-2xl backdrop-blur-sm border border-gray-800">
              <div className="text-center">
                <h2 className="text-3xl font-bold tracking-tight text-[var(--text-primary)]">Welcome to LegalGPT</h2>
                <p className="mt-2 text-[var(--text-secondary)]">Your virtual legal assistant.</p>
              </div>
              <div className="space-y-6">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-gray-700"></span>
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-gray-900/50 px-2 text-[var(--text-secondary)]">Sign in with email</span>
                  </div>
                </div>
                <form className="space-y-4" onSubmit={onSubmit}>
                  <div>
                    <label className="sr-only" htmlFor="email">Email address</label>
                    <input autoComplete="email" className="relative block w-full appearance-none rounded-lg border border-gray-700 bg-gray-800 px-3 py-3 text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:z-10 focus:border-[var(--primary-color)] focus:outline-none focus:ring-[var(--primary-color)] sm:text-sm" id="email" name="email" placeholder="Email address" required type="email" value={email} onChange={(e)=>setEmail(e.target.value)} />
                  </div>
                  <div>
                    <label className="sr-only" htmlFor="password">Password</label>
                    <input autoComplete="current-password" className="relative block w-full appearance-none rounded-lg border border-gray-700 bg-gray-800 px-3 py-3 text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:z-10 focus:border-[var(--primary-color)] focus:outline-none focus:ring-[var(--primary-color)] sm:text-sm" id="password" name="password" placeholder="Password" required type="password" value={password} onChange={(e)=>setPassword(e.target.value)} />
                  </div>
                  <div>
                    <button className="w-full inline-flex justify-center rounded-lg bg-[var(--primary-color)] px-4 py-3 text-sm font-semibold text-black transition-colors hover:bg-[var(--accent-color)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-color)] focus:ring-offset-2 focus:ring-offset-gray-900" type="submit" disabled={loading}>
                      {loading ? 'Signing in...' : 'Sign in'}
                    </button>
                  </div>
                  {error && <p className="text-red-400 text-sm">{error}</p>}
                </form>
              </div>
              <p className="mt-6 text-center text-sm text-[var(--text-secondary)]">
                New to LegalGPT?
                <Link to="/register" className="font-medium text-[var(--primary-color)] hover:underline ml-1">Create an account</Link>
              </p>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default Login;


