// pages/Transfer.jsx — Money Transfer Page
// ==========================================
// Two types of transfers:
//   1. Bank Transfer   — send money using the recipient's 12-digit account number
//   2. Web ID Transfer — send money using the recipient's short Web ID (like UPI)
//
// Features:
//   - Tab switching between transfer modes
//   - Live recipient lookup (shows name before confirming)
//   - Amount validation
//   - Success confirmation with reference number

import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import api from '../api/axios'
import Navbar from '../components/Navbar'
import toast from 'react-hot-toast'
import {
  Hash, Zap, ArrowUpRight, CheckCircle, X,
  User, DollarSign, FileText, ArrowLeft,
} from 'lucide-react'

function Transfer() {
  const location = useLocation()
  const navigate = useNavigate()

  // Active tab: 'bank' or 'webid'
  const [activeTab, setActiveTab] = useState('bank')

  // Bank Transfer form
  const [bankForm, setBankForm] = useState({
    recipient_account_number: '',
    amount: '',
    description: '',
  })

  // Web ID Transfer form
  const [webidForm, setWebidForm] = useState({
    recipient_web_id: '',
    amount: '',
    description: '',
  })

  // Recipient info (shown after lookup)
  const [recipientInfo, setRecipientInfo] = useState(null)
  const [lookupLoading, setLookupLoading] = useState(false)

  // Transfer result
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState({})

  // User's current balance
  const [myBalance, setMyBalance] = useState(null)

  // Read ?tab=webid from URL (set by Dashboard quick actions)
  useEffect(() => {
    const params = new URLSearchParams(location.search)
    if (params.get('tab') === 'webid') setActiveTab('webid')
  }, [location])

  // Load user's balance
  useEffect(() => {
    api.get('/dashboard/').then(r => {
      setMyBalance(r.data.data?.account?.balance)
    }).catch(() => {})
  }, [])

  // Reset recipient info when tab changes
  const handleTabChange = (tab) => {
    setActiveTab(tab)
    setRecipientInfo(null)
    setResult(null)
    setErrors({})
  }

  // ============================================
  // LIVE LOOKUP — Account Number
  // ============================================
  const lookupByAccount = async (accountNumber) => {
    if (accountNumber.length !== 12) {
      setRecipientInfo(null)
      return
    }
    setLookupLoading(true)
    try {
      const res = await api.get(`/lookup/account/${accountNumber}/`)
      setRecipientInfo(res.data.data)
    } catch {
      setRecipientInfo(null)
    } finally {
      setLookupLoading(false)
    }
  }

  // ============================================
  // LIVE LOOKUP — Web ID
  // ============================================
  const lookupByWebId = async (webId) => {
    if (webId.length < 4) {
      setRecipientInfo(null)
      return
    }
    setLookupLoading(true)
    try {
      const res = await api.get(`/lookup/webid/${webId}/`)
      setRecipientInfo(res.data.data)
    } catch {
      setRecipientInfo(null)
    } finally {
      setLookupLoading(false)
    }
  }

  // Handle bank form changes
  const handleBankChange = (e) => {
    const { name, value } = e.target
    setBankForm(prev => ({ ...prev, [name]: value }))
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }))

    if (name === 'recipient_account_number') {
      setRecipientInfo(null)
      if (value.length === 12) lookupByAccount(value)
    }
  }

  // Handle Web ID form changes
  const handleWebIdChange = (e) => {
    const { name, value } = e.target
    setWebidForm(prev => ({ ...prev, [name]: value }))
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }))

    if (name === 'recipient_web_id') {
      setRecipientInfo(null)
      if (value.length >= 4) lookupByWebId(value)
    }
  }

  // ============================================
  // SUBMIT — Bank Transfer
  // ============================================
  const handleBankSubmit = async (e) => {
    e.preventDefault()
    setErrors({})

    const newErrors = {}
    if (!bankForm.recipient_account_number || bankForm.recipient_account_number.length !== 12) {
      newErrors.recipient_account_number = 'Enter a valid 12-digit account number'
    }
    if (!bankForm.amount || parseFloat(bankForm.amount) <= 0) {
      newErrors.amount = 'Enter a valid amount'
    }
    if (myBalance && parseFloat(bankForm.amount) > parseFloat(myBalance)) {
      newErrors.amount = `Insufficient balance. Your balance is ₹${parseFloat(myBalance).toLocaleString('en-IN')}`
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    setIsLoading(true)
    try {
      const response = await api.post('/transfer/bank/', {
        recipient_account_number: bankForm.recipient_account_number,
        amount: parseFloat(bankForm.amount),
        description: bankForm.description,
      })
      setResult(response.data.data)
      setMyBalance(response.data.data.new_balance)
      toast.success('Transfer successful! 🎉')
    } catch (error) {
      const msg = error.response?.data?.message || 'Transfer failed. Please try again.'
      toast.error(msg)
      setErrors({ general: msg })
    } finally {
      setIsLoading(false)
    }
  }

  // ============================================
  // SUBMIT — Web ID Transfer
  // ============================================
  const handleWebIdSubmit = async (e) => {
    e.preventDefault()
    setErrors({})

    const newErrors = {}
    if (!webidForm.recipient_web_id) {
      newErrors.recipient_web_id = 'Enter a Web ID'
    }
    if (!webidForm.amount || parseFloat(webidForm.amount) <= 0) {
      newErrors.amount = 'Enter a valid amount'
    }
    if (myBalance && parseFloat(webidForm.amount) > parseFloat(myBalance)) {
      newErrors.amount = `Insufficient balance. Your balance is ₹${parseFloat(myBalance).toLocaleString('en-IN')}`
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    setIsLoading(true)
    try {
      const response = await api.post('/transfer/webid/', {
        recipient_web_id: webidForm.recipient_web_id.toLowerCase().trim(),
        amount: parseFloat(webidForm.amount),
        description: webidForm.description,
      })
      setResult(response.data.data)
      setMyBalance(response.data.data.new_balance)
      toast.success('Transfer successful! 🎉')
    } catch (error) {
      const msg = error.response?.data?.message || 'Transfer failed. Please try again.'
      toast.error(msg)
      setErrors({ general: msg })
    } finally {
      setIsLoading(false)
    }
  }

  // ============================================
  // SUCCESS SCREEN
  // ============================================
  if (result) {
    const txn = result.transaction
    return (
      <div className="page">
        <Navbar />
        <div className="container page-content">
          <div style={{ maxWidth: 500, margin: '40px auto', textAlign: 'center' }}>
            <div style={{
              width: 80, height: 80,
              background: 'linear-gradient(135deg, #10b981, #059669)',
              borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 24px',
              boxShadow: '0 8px 32px rgba(16, 185, 129, 0.3)',
            }}>
              <CheckCircle size={44} color="white" />
            </div>

            <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8 }}>Transfer Successful!</h1>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 32 }}>
              Your money has been sent.
            </p>

            {/* Receipt */}
            <div className="card" style={{ textAlign: 'left', marginBottom: 24 }}>
              {[
                { label: 'Reference Number', value: txn.reference_number },
                { label: 'Amount Sent', value: `₹${parseFloat(txn.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`, bold: true, color: 'var(--red)' },
                { label: 'To', value: txn.receiver_name },
                { label: 'Account', value: txn.receiver_account },
                { label: 'Transfer Type', value: txn.transfer_type === 'webid' ? 'Web ID Transfer' : 'Bank Transfer' },
                { label: 'Your New Balance', value: `₹${parseFloat(result.new_balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`, bold: true, color: 'var(--green)' },
              ].map((row, i) => (
                <div key={i} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '10px 0',
                  borderBottom: i < 5 ? '1px solid var(--border-subtle)' : 'none',
                }}>
                  <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{row.label}</span>
                  <span style={{
                    fontSize: 14,
                    fontWeight: row.bold ? 700 : 500,
                    color: row.color || 'var(--text-primary)',
                    fontFamily: row.label === 'Reference Number' ? 'monospace' : 'inherit',
                    letterSpacing: row.label === 'Reference Number' ? 1 : 0,
                  }}>
                    {row.value}
                  </span>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', gap: 12 }}>
              <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => { setResult(null); setBankForm({ recipient_account_number: '', amount: '', description: '' }); setWebidForm({ recipient_web_id: '', amount: '', description: '' }); setRecipientInfo(null) }}>
                <ArrowLeft size={16} /> New Transfer
              </button>
              <button className="btn btn-primary" style={{ flex: 1 }} onClick={() => navigate('/dashboard')}>
                Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // ============================================
  // MAIN TRANSFER FORM
  // ============================================
  return (
    <div className="page">
      <Navbar />
      <div className="container page-content">
        <div className="page-header">
          <h1 className="page-title">Send <span>Money</span></h1>
          <p className="page-description">
            Transfer funds instantly using an account number or Web ID.
            {myBalance && (
              <span style={{ marginLeft: 12, color: 'var(--gold-primary)', fontWeight: 600 }}>
                Balance: ₹{parseFloat(myBalance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
            )}
          </p>
        </div>

        <div style={{ maxWidth: 560, margin: '0 auto' }}>
          {/* Transfer Type Tabs */}
          <div className="transfer-tabs">
            <button
              className={`transfer-tab ${activeTab === 'bank' ? 'active' : ''}`}
              onClick={() => handleTabChange('bank')}
            >
              <Hash size={16} />
              Bank Transfer
            </button>
            <button
              className={`transfer-tab ${activeTab === 'webid' ? 'active' : ''}`}
              onClick={() => handleTabChange('webid')}
            >
              <Zap size={16} />
              Web ID Transfer
            </button>
          </div>

          <div className="card">
            {/* ── BANK TRANSFER FORM ── */}
            {activeTab === 'bank' && (
              <form onSubmit={handleBankSubmit} noValidate>
                <div className="card-title" style={{ marginBottom: 4 }}>Bank Transfer</div>
                <p className="card-subtitle">Send money using the recipient's 12-digit account number.</p>

                {/* Account Number */}
                <div className="form-group">
                  <label className="form-label" htmlFor="account_number">
                    Recipient Account Number
                  </label>
                  <div className="input-with-icon">
                    <Hash size={16} className="input-icon" />
                    <input
                      id="account_number"
                      name="recipient_account_number"
                      type="text"
                      maxLength={12}
                      className={`form-input ${errors.recipient_account_number ? 'error' : ''}`}
                      placeholder="Enter 12-digit account number"
                      value={bankForm.recipient_account_number}
                      onChange={handleBankChange}
                      style={{ fontFamily: 'monospace', letterSpacing: 2 }}
                    />
                  </div>
                  {errors.recipient_account_number && (
                    <p className="form-error">{errors.recipient_account_number}</p>
                  )}
                  <p className="form-hint">
                    {bankForm.recipient_account_number.length}/12 digits
                    {lookupLoading && ' · Looking up...'}
                  </p>
                </div>

                {/* Recipient Preview */}
                {recipientInfo && (
                  <div className="recipient-preview">
                    <div className="recipient-avatar">
                      {recipientInfo.full_name?.[0]?.toUpperCase()}
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: 14 }}>{recipientInfo.full_name}</div>
                      <div style={{ fontSize: 12, color: 'var(--green)' }}>✓ Account verified</div>
                    </div>
                  </div>
                )}

                {/* Amount */}
                <div className="form-group">
                  <label className="form-label" htmlFor="bank_amount">Amount (₹)</label>
                  <div className="input-with-icon">
                    <DollarSign size={16} className="input-icon" />
                    <input
                      id="bank_amount"
                      name="amount"
                      type="number"
                      min="1"
                      step="0.01"
                      className={`form-input ${errors.amount ? 'error' : ''}`}
                      placeholder="0.00"
                      value={bankForm.amount}
                      onChange={handleBankChange}
                    />
                  </div>
                  {errors.amount && <p className="form-error">{errors.amount}</p>}

                  {/* Quick amount buttons */}
                  <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                    {[100, 500, 1000, 5000].map(amt => (
                      <button
                        key={amt}
                        type="button"
                        className="btn btn-ghost btn-sm"
                        onClick={() => setBankForm(prev => ({ ...prev, amount: amt }))}
                        style={{ padding: '4px 10px', fontSize: 12 }}
                      >
                        ₹{amt}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Description */}
                <div className="form-group">
                  <label className="form-label" htmlFor="bank_desc">Note (Optional)</label>
                  <div className="input-with-icon">
                    <FileText size={16} className="input-icon" />
                    <input
                      id="bank_desc"
                      name="description"
                      type="text"
                      className="form-input"
                      placeholder="e.g., Rent, Dinner split..."
                      value={bankForm.description}
                      onChange={handleBankChange}
                      maxLength={100}
                    />
                  </div>
                </div>

                {errors.general && (
                  <div className="alert alert-error" style={{ marginBottom: 16 }}>
                    <X size={16} /> {errors.general}
                  </div>
                )}

                <button
                  type="submit"
                  className="btn btn-primary btn-full btn-lg"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <><span className="spinner"></span> Processing...</>
                  ) : (
                    <><ArrowUpRight size={18} /> Send ₹{bankForm.amount || '0'}</>
                  )}
                </button>
              </form>
            )}

            {/* ── WEB ID TRANSFER FORM ── */}
            {activeTab === 'webid' && (
              <form onSubmit={handleWebIdSubmit} noValidate>
                <div className="card-title" style={{ marginBottom: 4 }}>Web ID Transfer</div>
                <p className="card-subtitle">Send money using the recipient's unique Web ID (like UPI).</p>

                {/* Web ID */}
                <div className="form-group">
                  <label className="form-label" htmlFor="web_id">Recipient Web ID</label>
                  <div className="input-with-icon">
                    <Zap size={16} className="input-icon" />
                    <input
                      id="web_id"
                      name="recipient_web_id"
                      type="text"
                      className={`form-input ${errors.recipient_web_id ? 'error' : ''}`}
                      placeholder="e.g., john1abc"
                      value={webidForm.recipient_web_id}
                      onChange={handleWebIdChange}
                      style={{ paddingLeft: 44 }}
                    />
                  </div>
                  {errors.recipient_web_id && (
                    <p className="form-error">{errors.recipient_web_id}</p>
                  )}
                  <p className="form-hint">
                    Ask the recipient for their Web ID from their dashboard.
                    {lookupLoading && ' · Looking up...'}
                  </p>
                </div>

                {/* Recipient Preview */}
                {recipientInfo && (
                  <div className="recipient-preview">
                    <div className="recipient-avatar">
                      {recipientInfo.full_name?.[0]?.toUpperCase()}
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: 14 }}>{recipientInfo.full_name}</div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                        Web ID: @{recipientInfo.web_id}
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--green)' }}>✓ User verified</div>
                    </div>
                  </div>
                )}

                {/* Amount */}
                <div className="form-group">
                  <label className="form-label" htmlFor="webid_amount">Amount (₹)</label>
                  <div className="input-with-icon">
                    <DollarSign size={16} className="input-icon" />
                    <input
                      id="webid_amount"
                      name="amount"
                      type="number"
                      min="1"
                      step="0.01"
                      className={`form-input ${errors.amount ? 'error' : ''}`}
                      placeholder="0.00"
                      value={webidForm.amount}
                      onChange={handleWebIdChange}
                    />
                  </div>
                  {errors.amount && <p className="form-error">{errors.amount}</p>}

                  <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                    {[100, 500, 1000, 5000].map(amt => (
                      <button
                        key={amt}
                        type="button"
                        className="btn btn-ghost btn-sm"
                        onClick={() => setWebidForm(prev => ({ ...prev, amount: amt }))}
                        style={{ padding: '4px 10px', fontSize: 12 }}
                      >
                        ₹{amt}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Description */}
                <div className="form-group">
                  <label className="form-label" htmlFor="webid_desc">Note (Optional)</label>
                  <div className="input-with-icon">
                    <FileText size={16} className="input-icon" />
                    <input
                      id="webid_desc"
                      name="description"
                      type="text"
                      className="form-input"
                      placeholder="e.g., Splitting the bill"
                      value={webidForm.description}
                      onChange={handleWebIdChange}
                      maxLength={100}
                    />
                  </div>
                </div>

                {/* Web ID explanation */}
                <div className="alert alert-gold" style={{ marginBottom: 16, fontSize: 12 }}>
                  <Zap size={14} />
                  <span>
                    <strong>What is a Web ID?</strong> It's a short unique ID like "@john1abc" that every SecureBank user gets. Find it on your Dashboard.
                  </span>
                </div>

                {errors.general && (
                  <div className="alert alert-error" style={{ marginBottom: 16 }}>
                    <X size={16} /> {errors.general}
                  </div>
                )}

                <button
                  type="submit"
                  className="btn btn-primary btn-full btn-lg"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <><span className="spinner"></span> Processing...</>
                  ) : (
                    <><Zap size={18} /> Send ₹{webidForm.amount || '0'}</>
                  )}
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Transfer
