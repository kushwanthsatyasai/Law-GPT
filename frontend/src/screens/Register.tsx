import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const API_BASE = '/api';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, role: 'user' })
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      navigate('/dashboard');
    } catch (err: any) {
      setError('Registration failed: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  }
  return (
    <div className="bg-[var(--background-color)] text-[var(--text-primary)] min-h-screen flex items-center justify-center bg-grid-pattern">
      <div className="w-full max-w-md p-8 space-y-8 bg-[var(--background-color)] rounded-2xl shadow-2xl shadow-black/30 border border-[var(--border-color)]">
        <div className="flex flex-col items-center">
          <svg className="w-12 h-12 text-[var(--primary-color)] mb-4" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M21.93,10.29,18,6.34V3a1,1,0,0,0-2,0V5.41l-2.29-2.29a1,1,0,0,0-1.42,0L3.71,11.71a1,1,0,0,0,0,1.41L5.12,14.54,2.29,17.36a1,1,0,0,0,0,1.42L3.7,20.19a1,1,0,0,0,1.41,0l2.83-2.83,1.41,1.41a1,1,0,0,0,1.42,0L18.88,10.29,18,9.41,13.41,14,12,12.59,16.59,8l1,1,3-3-1.71-1.71ZM6.54,12.41,4.41,10.29,12,2.71l2.12,2.12Z"></path>
          </svg>
          <h1 className="text-3xl font-bold text-center">Create Your Account</h1>
          <p className="text-center text-[var(--text-secondary)] mt-2">Join the future of legal assistance.</p>
        </div>
        <form className="space-y-6" onSubmit={onSubmit}>
          <div>
            <label className="block mb-2" htmlFor="email">Email</label>
            <input className="w-full p-3 bg-[var(--input-bg-color)] border border-[var(--border-color)] rounded-lg text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:border-[var(--primary-color)] focus:ring-1 focus:ring-[var(--primary-color)] transition-colors" id="email" name="email" placeholder="you@example.com" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div>
            <label className="block mb-2" htmlFor="password">Password</label>
            <input className="w-full p-3 bg-[var(--input-bg-color)] border border-[var(--border-color)] rounded-lg text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:border-[var(--primary-color)] focus:ring-1 focus:ring-[var(--primary-color)] transition-colors" id="password" name="password" placeholder="••••••••" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <div>
            <label className="block mb-2" htmlFor="confirm-password">Confirm Password</label>
            <input className="w-full p-3 bg-[var(--input-bg-color)] border border-[var(--border-color)] rounded-lg text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:border-[var(--primary-color)] focus:ring-1 focus:ring-[var(--primary-color)] transition-colors" id="confirm-password" name="confirm-password" placeholder="••••••••" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
          </div>
          <div>
            <button type="submit" className="w-full inline-flex justify-center bg-[var(--primary-color)] text-black py-3 px-6 rounded-lg font-bold hover:bg-[var(--secondary-color)] transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-[var(--primary-color)] focus:ring-opacity-50" disabled={loading}>
              {loading ? 'Registering...' : 'Register'}
            </button>
          </div>
          {error && <p className="text-red-400 text-sm">{error}</p>}
        </form>
        <p className="text-center text-sm text-[var(--text-secondary)]">
          Already have an account?
          <Link to="/" className="font-medium text-[var(--primary-color)] hover:underline ml-1">Log in</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;


