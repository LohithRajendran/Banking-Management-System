import React, { useState, useEffect, useContext } from 'react';
import api from '../api/axios';
import { AuthContext } from '../context/AuthContext';

export default function DashboardPage() {
  const { user, logout } = useContext(AuthContext);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/accounts/')
      .then((res) => setAccounts(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const totalBalance = accounts.reduce((acc, a) => acc + parseFloat(a.balance), 0);

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>Welcome back, {user?.email}</h2>
          <p style={{ color: 'var(--text-muted)' }}>Banking Overview Dashboard</p>
        </div>
        <button onClick={logout} className="btn-primary" style={{ backgroundColor: 'var(--accent-rose)' }}>
          Sign Out
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Total Combined Balance</p>
          <h1 style={{ color: 'var(--accent-emerald)', marginTop: '0.5rem' }}>${totalBalance.toFixed(2)}</h1>
        </div>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Active Accounts</p>
          <h1 style={{ color: 'var(--accent-blue)', marginTop: '0.5rem' }}>{accounts.length}</h1>
        </div>
      </div>

      <h3 style={{ marginBottom: '1rem' }}>Your Accounts</h3>
      {loading ? (
        <p>Loading accounts...</p>
      ) : accounts.length === 0 ? (
        <div className="card"><p>No accounts found. Create your first savings or current account!</p></div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
          {accounts.map((acc) => (
            <div key={acc.id} className="card">
              <span style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem', borderRadius: '4px', backgroundColor: 'var(--accent-purple)', textTransform: 'uppercase' }}>
                {acc.account_type}
              </span>
              <h4 style={{ marginTop: '0.5rem' }}>Acc #: {acc.account_number}</h4>
              <h2 style={{ color: 'var(--accent-emerald)', margin: '0.5rem 0' }}>${acc.balance}</h2>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Min Balance: ${acc.min_balance}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
