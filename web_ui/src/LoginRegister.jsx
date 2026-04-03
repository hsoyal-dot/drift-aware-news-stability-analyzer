import { useState } from 'react';
import { useAuth } from './AuthContext';
import './index.css';

function LoginRegister() {
  const { login } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        // Login Request
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch('http://localhost:8000/api/auth/token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Invalid credentials');
        }

        const data = await response.json();
        login(data.access_token);
      } else {
        // Register Request
        const response = await fetch('http://localhost:8000/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ username, password }),
        });

        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || 'Registration failed');
        }

        // Auto-login after register
        setIsLogin(true);
        setError('Registration successful! Please login.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <h1>Welcome to DANSA</h1>
      <p className="description">
        Secure access required. Please sign in to use the Drift-Aware News Stability Analyzer.
      </p>

      <div className="glass-panel" style={{ maxWidth: '400px', margin: '0 auto' }}>
        <div className="tabs-container" style={{ marginBottom: '2rem' }}>
          <button 
            className={`tab-button ${isLogin ? 'active' : ''}`}
            onClick={() => {setIsLogin(true); setError('');}}
          >
            Log In
          </button>
          <button 
            className={`tab-button ${!isLogin ? 'active' : ''}`}
            onClick={() => {setIsLogin(false); setError('');}}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <label style={{ display: 'block', color: '#94a3b8', marginBottom: '0.5rem', fontSize: '0.9em' }}>Username</label>
            <input 
              type="text" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required 
              style={{
                width: '100%',
                background: 'rgba(0, 0, 0, 0.2)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                color: '#e5e7eb',
                padding: '0.8rem',
                fontFamily: 'inherit',
                fontSize: '1rem',
                outline: 'none',
                boxSizing: 'border-box'
              }} 
            />
          </div>

          <div>
            <label style={{ display: 'block', color: '#94a3b8', marginBottom: '0.5rem', fontSize: '0.9em' }}>Password</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
              style={{
                width: '100%',
                background: 'rgba(0, 0, 0, 0.2)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                color: '#e5e7eb',
                padding: '0.8rem',
                fontFamily: 'inherit',
                fontSize: '1rem',
                outline: 'none',
                boxSizing: 'border-box'
              }} 
            />
          </div>

          {error && <div style={{ color: error.includes('successful') ? '#4ade80' : '#ef4444', textAlign: 'center' }}>{error}</div>}

          <button type="submit" disabled={loading || !username || !password}>
            {loading ? <span className="loading-spinner" style={{width: '15px', height: '15px'}}></span> : null}
            {isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>
      </div>
    </>
  );
}

export default LoginRegister;
