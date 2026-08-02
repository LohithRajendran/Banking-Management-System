// pages/History.jsx — Transaction History Page
// ===============================================
// Shows ALL transactions (sent and received) for the current user.
// Features:
//   - Filter by All / Sent / Received / Bank / Web ID
//   - Color-coded sent (red) vs received (green)
//   - Transaction reference numbers
//   - Date and time

import { useState, useEffect } from 'react'
import api from '../api/axios'
import Navbar from '../components/Navbar'
import {
  ArrowUpRight, ArrowDownLeft, Hash, Zap,
  RefreshCw, Filter, Search,
} from 'lucide-react'
import toast from 'react-hot-toast'

function History() {
  const [transactions, setTransactions] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [myAccountNumber, setMyAccountNumber] = useState(null)
  const [filter, setFilter] = useState('all')  // 'all', 'sent', 'received', 'bank', 'webid'
  const [searchTerm, setSearchTerm] = useState('')
  const [totalCount, setTotalCount] = useState(0)

  const loadTransactions = async (showRefresh = false) => {
    if (showRefresh) setIsRefreshing(true)
    try {
      const response = await api.get('/transactions/')
      const data = response.data.data
      setTransactions(data.transactions)
      setMyAccountNumber(data.account_number)
      setTotalCount(data.total)
    } catch (error) {
      toast.error('Failed to load transactions.')
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    loadTransactions()
  }, [])

  // Format date and time
  const formatDateTime = (isoString) => {
    const date = new Date(isoString)
    return {
      date: date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }),
      time: date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
    }
  }

  // Filter and search logic
  const filteredTransactions = transactions.filter(txn => {
    const isSent = txn.sender_account === myAccountNumber

    if (filter === 'sent' && !isSent) return false
    if (filter === 'received' && isSent) return false
    if (filter === 'bank' && txn.transfer_type !== 'bank') return false
    if (filter === 'webid' && txn.transfer_type !== 'webid') return false

    if (searchTerm) {
      const search = searchTerm.toLowerCase()
      return (
        txn.sender_name.toLowerCase().includes(search) ||
        txn.receiver_name.toLowerCase().includes(search) ||
        txn.reference_number.toLowerCase().includes(search) ||
        txn.description?.toLowerCase().includes(search) ||
        txn.sender_account.includes(search) ||
        txn.receiver_account.includes(search)
      )
    }
    return true
  })

  // Calculate summary stats
  const stats = transactions.reduce((acc, txn) => {
    const isSent = txn.sender_account === myAccountNumber
    if (isSent) {
      acc.totalSent += parseFloat(txn.amount)
      acc.sentCount++
    } else {
      acc.totalReceived += parseFloat(txn.amount)
      acc.receivedCount++
    }
    return acc
  }, { totalSent: 0, totalReceived: 0, sentCount: 0, receivedCount: 0 })

  const filters = [
    { key: 'all', label: 'All', count: totalCount },
    { key: 'sent', label: 'Sent', count: stats.sentCount },
    { key: 'received', label: 'Received', count: stats.receivedCount },
    { key: 'bank', label: 'Bank', count: null },
    { key: 'webid', label: 'Web ID', count: null },
  ]

  if (isLoading) {
    return (
      <div className="page">
        <Navbar />
        <div className="page-loading">
          <div className="spinner spinner-light" style={{ width: 40, height: 40 }}></div>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>Loading transactions...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="page">
      <Navbar />
      <div className="container page-content">

        {/* Page Header */}
        <div className="page-header" style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <div>
            <h1 className="page-title">Transaction <span>History</span></h1>
            <p className="page-description">{totalCount} total transactions</p>
          </div>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => loadTransactions(true)}
            disabled={isRefreshing}
            style={{ marginTop: 4 }}
          >
            <RefreshCw size={14} className={isRefreshing ? 'animate-pulse' : ''} />
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        {/* ── SUMMARY CARDS ── */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
          <div className="card" style={{ borderColor: 'rgba(239,68,68,0.2)' }}>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 600, marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.5 }}>
              Total Sent
            </div>
            <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--red)' }}>
              ₹{stats.totalSent.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
              {stats.sentCount} outgoing transfer{stats.sentCount !== 1 ? 's' : ''}
            </div>
          </div>

          <div className="card" style={{ borderColor: 'rgba(16,185,129,0.2)' }}>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 600, marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.5 }}>
              Total Received
            </div>
            <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--green)' }}>
              ₹{stats.totalReceived.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
              {stats.receivedCount} incoming transfer{stats.receivedCount !== 1 ? 's' : ''}
            </div>
          </div>
        </div>

        {/* ── SEARCH ── */}
        <div style={{ position: 'relative', marginBottom: 16 }}>
          <Search size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', pointerEvents: 'none' }} />
          <input
            type="text"
            className="form-input"
            placeholder="Search by name, account, reference..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            style={{ paddingLeft: 44 }}
          />
        </div>

        {/* ── FILTER TABS ── */}
        <div className="filter-tabs">
          {filters.map(f => (
            <button
              key={f.key}
              className={`filter-tab ${filter === f.key ? 'active' : ''}`}
              onClick={() => setFilter(f.key)}
            >
              {f.label}
              {f.count !== null && (
                <span style={{
                  marginLeft: 6, fontSize: 11, fontWeight: 700,
                  background: filter === f.key ? 'rgba(0,0,0,0.2)' : 'var(--bg-secondary)',
                  padding: '1px 6px', borderRadius: 999,
                }}>
                  {f.count}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* ── TRANSACTION LIST ── */}
        {filteredTransactions.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📭</div>
            <p className="empty-state-title">
              {searchTerm ? 'No matching transactions' : 'No transactions yet'}
            </p>
            <p className="empty-state-text">
              {searchTerm
                ? 'Try a different search term.'
                : 'Make your first transfer to see it here.'}
            </p>
          </div>
        ) : (
          <div className="transaction-list">
            {filteredTransactions.map(txn => {
              const isSent = txn.sender_account === myAccountNumber
              const { date, time } = formatDateTime(txn.timestamp)
              const otherPerson = isSent ? txn.receiver_name : txn.sender_name
              const otherAccount = isSent ? txn.receiver_account : txn.sender_account

              return (
                <div key={txn.id} className="transaction-item">
                  {/* Direction Icon */}
                  <div className={`transaction-icon ${isSent ? 'sent' : 'received'}`}>
                    {isSent
                      ? <ArrowUpRight size={20} />
                      : <ArrowDownLeft size={20} />
                    }
                  </div>

                  {/* Transaction Info */}
                  <div className="transaction-info">
                    <div className="transaction-name">
                      {isSent ? `Sent to ${otherPerson}` : `Received from ${otherPerson}`}
                    </div>
                    <div className="transaction-meta" style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                      {/* Transfer type badge */}
                      <span style={{
                        display: 'inline-flex', alignItems: 'center', gap: 3,
                        padding: '2px 7px',
                        background: txn.transfer_type === 'webid' ? 'var(--gold-glow)' : 'var(--blue-bg)',
                        color: txn.transfer_type === 'webid' ? 'var(--gold-primary)' : 'var(--blue)',
                        borderRadius: 999, fontSize: 10, fontWeight: 700,
                      }}>
                        {txn.transfer_type === 'webid' ? <Zap size={10} /> : <Hash size={10} />}
                        {txn.transfer_type === 'webid' ? 'Web ID' : 'Bank'}
                      </span>
                      <span style={{ color: 'var(--text-muted)', fontSize: 11, fontFamily: 'monospace' }}>
                        {otherAccount}
                      </span>
                      <span style={{ color: 'var(--text-muted)', fontSize: 11 }}>
                        {date} · {time}
                      </span>
                      {txn.description && (
                        <span style={{ color: 'var(--text-secondary)', fontSize: 11 }}>
                          "{txn.description}"
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Amount */}
                  <div style={{ textAlign: 'right', flexShrink: 0 }}>
                    <div className={`transaction-amount ${isSent ? 'sent' : 'received'}`}>
                      {isSent ? '-' : '+'}₹{parseFloat(txn.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </div>
                    <div className="transaction-ref">{txn.reference_number}</div>
                    <span className="badge badge-success" style={{ fontSize: 10, padding: '1px 6px', marginTop: 4 }}>
                      {txn.status}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

export default History
