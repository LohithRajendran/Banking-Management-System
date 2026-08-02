// pages/CreateAccount.jsx — Create Bank Account Page
// =====================================================
// After signup, new users land here to create their bank account.
// One click creates an account with a unique 12-digit account number
// and a unique Web ID. New accounts start with ₹1000 welcome bonus.

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'
import toast from 'react-hot-toast'
import {
  Building2, CreditCard, Hash, Zap, ArrowRight, Copy, CheckCheck,
} from 'lucide-react'

function CreateAccount() {
  const { user, updateUser } = useAuth()
  const navigate = useNavigate()

  const [isLoading, setIsLoading] = useState(false)
  const [account, setAccount] = useState(null)  // Created account details
  const [copied, setCopied] = useState('')

  const handleCreateAccount = async () => {
    setIsLoading(true)
    try {
      const response = await api.post('/create-account/')
      setAccount(response.data.data)
      toast.success('🎉 Bank account created! You received ₹1,000 welcome bonus!')
    } catch (error) {
      const msg = error.response?.data?.message || 'Failed to create account.'
      toast.error(msg)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCopy = (text, label) => {
    navigator.clipboard.writeText(text)
    setCopied(label)
    toast.success(`${label} copied!`)
    setTimeout(() => setCopied(''), 2000)
  }

  // If account was created, show the success screen
  if (account) {
    return (
      <div className="auth-page">
        <div className="auth-card" style={{ maxWidth: 520, textAlign: 'center' }}>
          {/* Success icon */}
          <div style={{
            width: 80, height: 80,
            background: 'linear-gradient(135deg, #10b981, #059669)',
            borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 24px',
            boxShadow: '0 8px 32px rgba(16, 185, 129, 0.3)',
            fontSize: 40,
          }}>
            🎉
          </div>

          <h1 className="auth-title" style={{ marginBottom: 8 }}>Account Created!</h1>
          <p className="auth-subtitle">Your banking account is ready to use</p>

          {/* Account details card */}
          <div style={{
            background: 'var(--bg-input)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: 24, marginTop: 24, textAlign: 'left',
          }}>
            {/* Account Number */}
            <div style={{ marginBottom: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <Hash size={14} color="var(--text-muted)" />
                <span className="form-label" style={{ margin: 0 }}>Account Number</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span className="account-number" style={{ fontSize: 22 }}>
                  {account.account_number}
                </span>
                <button
                  className="copy-btn"
                  onClick={() => handleCopy(account.account_number, 'Account number')}
                >
                  {copied === 'Account number' ? <CheckCheck size={12} /> : <Copy size={12} />}
                  {copied === 'Account number' ? 'Copied!' : 'Copy'}
                </button>
              </div>
            </div>

            {/* Web ID */}
            <div style={{ marginBottom: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <Zap size={14} color="var(--text-muted)" />
                <span className="form-label" style={{ margin: 0 }}>Your Web ID</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span className="web-id-badge">@{account.owner_web_id}</span>
                <button
                  className="copy-btn"
                  onClick={() => handleCopy(account.owner_web_id, 'Web ID')}
                >
                  {copied === 'Web ID' ? <CheckCheck size={12} /> : <Copy size={12} />}
                  {copied === 'Web ID' ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <p className="form-hint">Share your Web ID so others can send you money instantly.</p>
            </div>

            {/* Balance */}
            <div style={{
              background: 'linear-gradient(135deg, rgba(245,158,11,0.1), rgba(13,24,41,0.5))',
              border: '1px solid var(--border-gold)',
              borderRadius: 'var(--radius-md)',
              padding: 16,
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            }}>
              <div>
                <div style={{ fontSize: 12, color: 'var(--gold-dark)', fontWeight: 600, marginBottom: 4 }}>
                  WELCOME BONUS
                </div>
                <div style={{ fontSize: 28, fontWeight: 900, color: 'var(--text-primary)' }}>
                  <span style={{ color: 'var(--gold-primary)' }}>₹</span>
                  {parseFloat(account.balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
              </div>
              <span style={{ fontSize: 36 }}>🎁</span>
            </div>
          </div>

          <button
            className="btn btn-primary btn-full btn-lg"
            style={{ marginTop: 24 }}
            onClick={() => navigate('/dashboard')}
          >
            Go to Dashboard <ArrowRight size={18} />
          </button>
        </div>
      </div>
    )
  }

  // Initial screen — prompt to create account
  return (
    <div className="auth-page">
      <div className="auth-card" style={{ maxWidth: 480, textAlign: 'center' }}>

        <div style={{
          width: 80, height: 80,
          background: 'var(--gradient-gold)',
          borderRadius: '24px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 28px',
          boxShadow: 'var(--shadow-gold)',
        }}>
          <Building2 size={40} color="#000" strokeWidth={2} />
        </div>

        <h1 className="auth-title">Open Your Account</h1>
        <p className="auth-subtitle" style={{ marginBottom: 32 }}>
          Hello {user?.first_name}! One click to open your SecureBank account.
          <br />You'll receive a <strong style={{ color: 'var(--gold-primary)' }}>₹1,000 welcome bonus!</strong>
        </p>

        {/* Features list */}
        {[
          { icon: <Hash size={16} />, text: 'Unique 12-digit account number' },
          { icon: <Zap size={16} />, text: 'Personal Web ID for instant transfers' },
          { icon: <CreditCard size={16} />, text: '₹1,000 welcome bonus deposited instantly' },
        ].map((item, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'center', gap: 12,
            padding: '10px 16px',
            background: 'var(--bg-input)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            marginBottom: 10, textAlign: 'left',
            color: 'var(--text-secondary)', fontSize: 14,
          }}>
            <span style={{ color: 'var(--gold-primary)' }}>{item.icon}</span>
            {item.text}
          </div>
        ))}

        <button
          className="btn btn-primary btn-full btn-lg"
          style={{ marginTop: 24 }}
          onClick={handleCreateAccount}
          disabled={isLoading}
        >
          {isLoading ? (
            <><span className="spinner"></span> Creating your account...</>
          ) : (
            <>Open Bank Account <ArrowRight size={18} /></>
          )}
        </button>

      </div>
    </div>
  )
}

export default CreateAccount
