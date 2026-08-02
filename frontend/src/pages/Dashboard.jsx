// pages/Dashboard.jsx — Main Dashboard Page
// ============================================
// The home screen after login. Shows:
//   - Current balance (big gold card)
//   - Account number and Web ID
//   - Quick action buttons (Transfer, History, etc.)
//   - Recent transactions list

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'
import Navbar from '../components/Navbar'
import {
  ArrowUpRight, ArrowDownLeft, ArrowLeftRight, History,
  Copy, CheckCheck, Zap, Hash, RefreshCw, TrendingUp,
} from 'lucide-react'
import toast from 'react-hot-toast'

function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const [dashData, setDashData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [copiedItem, setCopiedItem] = useState('')

  const loadDashboard = async (showRefresh = false) => {
    if (showRefresh) setIsRefreshing(true)
    try {
      const response = await api.get('/dashboard/')
      setDashData(response.data.data)
    } catch (error) {
      toast.error('Failed to load dashboard. Please refresh.')
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  const handleCopy = (text, label) => {
    navigator.clipboard.writeText(text)
    setCopiedItem(label)
    toast.success(`${label} copied!`)
    setTimeout(() => setCopiedItem(''), 2000)
  }

  // Format balance with Indian number system (1,00,000)
  const formatBalance = (amount) => {
    return parseFloat(amount).toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  }

  // Format date to readable format
  const formatDate = (isoString) => {
    return new Date(isoString).toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
    })
  }

  // Format time
  const formatTime = (isoString) => {
    return new Date(isoString).toLocaleTimeString('en-IN', {
      hour: '2-digit', minute: '2-digit',
    })
  }

  // Loading skeleton
  if (isLoading) {
    return (
      <div className="page">
        <Navbar />
        <div className="page-loading">
          <div className="spinner spinner-light" style={{ width: 40, height: 40 }}></div>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  // No bank account — redirect to create account
  if (dashData && !dashData.has_bank_account) {
    return (
      <div className="page">
        <Navbar />
        <div className="container page-content">
          <div className="empty-state">
            <div className="empty-state-icon">🏦</div>
            <h2 className="empty-state-title">No Bank Account Yet</h2>
            <p className="empty-state-text">Open your bank account to start banking with SecureBank.</p>
            <button className="btn btn-primary btn-lg" onClick={() => navigate('/create-account')}>
              Open Bank Account
            </button>
          </div>
        </div>
      </div>
    )
  }

  const account = dashData?.account
  const recentTxns = dashData?.recent_transactions || []

  return (
    <div className="page">
      <Navbar />

      <div className="container page-content">
        {/* Page Header */}
        <div className="page-header" style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <div>
            <h1 className="page-title">
              Good {new Date().getHours() < 12 ? 'Morning' : new Date().getHours() < 17 ? 'Afternoon' : 'Evening'},{' '}
              <span>{user?.first_name}! 👋</span>
            </h1>
            <p className="page-description">Here's your financial overview for today.</p>
          </div>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => loadDashboard(true)}
            disabled={isRefreshing}
            style={{ marginTop: 4 }}
          >
            <RefreshCw size={14} className={isRefreshing ? 'animate-pulse' : ''} />
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        {/* ── BALANCE CARD ── */}
        <div className="balance-card animate-slideUp" style={{ marginBottom: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <div className="balance-label">Total Balance</div>
              <div className="balance-amount">
                <span className="currency">₹</span>
                {account ? formatBalance(account.balance) : '0.00'}
              </div>
              <div className="balance-account">
                Account:{' '}
                <span>{account?.account_number?.replace(/(.{4})/g, '$1 ').trim()}</span>
              </div>
            </div>

            {/* Web ID badge */}
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>Your Web ID</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexDirection: 'row-reverse' }}>
                <span className="web-id-badge" style={{ fontSize: 16 }}>
                  @{dashData?.user?.web_id}
                </span>
                <button
                  className="copy-btn"
                  onClick={() => handleCopy(dashData?.user?.web_id, 'Web ID')}
                >
                  {copiedItem === 'Web ID' ? <CheckCheck size={12} /> : <Copy size={12} />}
                </button>
              </div>
              <div style={{ marginTop: 8 }}>
                <button
                  className="copy-btn"
                  onClick={() => handleCopy(account?.account_number, 'Account number')}
                  style={{ fontSize: 11 }}
                >
                  {copiedItem === 'Account number' ? <CheckCheck size={12} /> : <Copy size={12} />}
                  {copiedItem === 'Account number' ? 'Copied!' : 'Copy account no.'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* ── QUICK ACTIONS ── */}
        <div className="card animate-slideUp" style={{ marginBottom: 20 }}>
          <h2 className="card-title" style={{ marginBottom: 16 }}>Quick Actions</h2>
          <div className="quick-actions">
            <button className="quick-action-btn" onClick={() => navigate('/transfer')}>
              <div className="quick-action-icon">
                <ArrowUpRight size={22} color="var(--gold-primary)" />
              </div>
              Send Money
            </button>
            <button className="quick-action-btn" onClick={() => navigate('/transfer?tab=webid')}>
              <div className="quick-action-icon">
                <Zap size={22} color="var(--gold-primary)" />
              </div>
              Web ID Pay
            </button>
            <button className="quick-action-btn" onClick={() => navigate('/history')}>
              <div className="quick-action-icon">
                <History size={22} color="var(--gold-primary)" />
              </div>
              History
            </button>
          </div>
        </div>

        {/* ── STATS ROW ── */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
          {/* Account Info */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
              <div className="stat-icon" style={{ background: 'var(--gold-glow)' }}>
                <Hash size={20} color="var(--gold-primary)" />
              </div>
              <div className="stat-label" style={{ margin: 0 }}>Account Number</div>
            </div>
            <div style={{ fontFamily: 'monospace', fontSize: 16, letterSpacing: 2, color: 'var(--gold-light)', fontWeight: 700 }}>
              {account?.account_number?.replace(/(.{4})/g, '$1 ').trim()}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6 }}>
              Opened {account ? formatDate(account.created_at) : '-'}
            </div>
          </div>

          {/* Status */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
              <div className="stat-icon" style={{ background: 'var(--green-bg)' }}>
                <TrendingUp size={20} color="var(--green)" />
              </div>
              <div className="stat-label" style={{ margin: 0 }}>Account Status</div>
            </div>
            <span className="badge badge-success" style={{ fontSize: 14, padding: '6px 14px' }}>
              ● Active
            </span>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>
              {recentTxns.length} recent transaction{recentTxns.length !== 1 ? 's' : ''}
            </div>
          </div>
        </div>

        {/* ── RECENT TRANSACTIONS ── */}
        <div className="card animate-fadeIn">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <h2 className="card-title" style={{ margin: 0 }}>Recent Transactions</h2>
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => navigate('/history')}
            >
              View All <ArrowLeftRight size={13} />
            </button>
          </div>

          {recentTxns.length === 0 ? (
            <div className="empty-state" style={{ padding: '40px 24px' }}>
              <div className="empty-state-icon" style={{ fontSize: 40 }}>💸</div>
              <p className="empty-state-title">No transactions yet</p>
              <p className="empty-state-text">Send money to someone to see transactions here.</p>
              <button className="btn btn-primary" onClick={() => navigate('/transfer')}>
                Make First Transfer
              </button>
            </div>
          ) : (
            <div className="transaction-list">
              {recentTxns.map(txn => {
                const isSent = txn.sender_account === account?.account_number
                return (
                  <div key={txn.id} className="transaction-item">
                    <div className={`transaction-icon ${isSent ? 'sent' : 'received'}`}>
                      {isSent ? <ArrowUpRight size={20} /> : <ArrowDownLeft size={20} />}
                    </div>
                    <div className="transaction-info">
                      <div className="transaction-name">
                        {isSent ? `To: ${txn.receiver_name}` : `From: ${txn.sender_name}`}
                      </div>
                      <div className="transaction-meta">
                        <span className="badge badge-info" style={{ fontSize: 10, padding: '2px 6px' }}>
                          {txn.transfer_type === 'webid' ? 'Web ID' : 'Bank'}
                        </span>
                        {' · '}{formatDate(txn.timestamp)} {formatTime(txn.timestamp)}
                        {txn.description && <> · {txn.description}</>}
                      </div>
                    </div>
                    <div>
                      <div className={`transaction-amount ${isSent ? 'sent' : 'received'}`}>
                        {isSent ? '-' : '+'}₹{parseFloat(txn.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </div>
                      <div className="transaction-ref">{txn.reference_number}</div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
