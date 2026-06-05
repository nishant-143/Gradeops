import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import Layout from '../components/Layout'
import ReviewCard from '../components/dashboard/ReviewCard'
import KeyboardShortcuts from '../components/dashboard/KeyboardShortcuts'
import { CheckCircle, XCircle, Clock, ChevronDown, Loader2, Keyboard } from 'lucide-react'
import { useGradeQueue } from '../hooks/useGradeQueue'
import { useGradeStore } from '../store/gradeStore'
import { useToast } from '../hooks'
import { examsAPI } from '../api'

export default function ReviewQueue() {
  const [searchParams, setSearchParams] = useSearchParams()
  const examId = searchParams.get('exam_id')
  const toast = useToast()
  const [showShortcuts, setShowShortcuts] = useState(false)

  const [exams, setExams] = useState([])
  const [loadingExams, setLoadingExams] = useState(true)

  const {
    gradeQueue, currentGrade, currentIndex,
    isLoading, nextGrade, previousGrade,
    approve, override, hasNext, hasPrev, progress,
  } = useGradeQueue(examId)

  const totalPending = useGradeStore(s => s.totalPending)
  const totalApproved = useGradeStore(s => s.totalApproved)
  const totalOverridden = useGradeStore(s => s.totalOverridden)

  /* Load exam list for selector */
  useEffect(() => {
    let isMounted = true
    ;(async () => {
      try {
        const data = await examsAPI.listExams()
        if (!isMounted) return
        const list = data.exams || []
        setExams(list)
        
        // auto-select first if none selected and we have exams
        if (!examId && list.length > 0 && list[0].id) {
          setSearchParams({ exam_id: list[0].id }, { replace: true })
        }
      } catch { /* silently fail */ }
      finally { if (isMounted) setLoadingExams(false) }
    })()
    return () => { isMounted = false }
  }, [examId, setSearchParams])

  /* Keyboard shortcuts */
  useEffect(() => {
    const handler = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return
      if (e.key === 'j' || e.key === 'J') { e.preventDefault(); nextGrade() }
      if (e.key === 'k' || e.key === 'K') { e.preventDefault(); previousGrade() }
      if (e.key === 'Enter') { e.preventDefault(); if (currentGrade) approve() }
      if (e.key === '?') { e.preventDefault(); setShowShortcuts(v => !v) }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [currentGrade, nextGrade, previousGrade, approve])

  const total   = totalPending + totalApproved + totalOverridden
  const donePct = total > 0 ? Math.round(((totalApproved + totalOverridden) / total) * 100) : 0

  const stats = [
    { label: 'Pending Review', value: totalPending,    icon: Clock,        bg: 'rgba(245,158,11,0.1)',  border: 'rgba(245,158,11,0.25)',  color: '#fcd34d' },
    { label: 'Approved',       value: totalApproved,   icon: CheckCircle,  bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.25)', color: '#6ee7b7' },
    { label: 'Overridden',     value: totalOverridden, icon: XCircle,      bg: 'rgba(239,68,68,0.1)',  border: 'rgba(239,68,68,0.25)',  color: '#fca5a5' },
  ]

  return (
    <Layout>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24, animation: 'slideUp 0.4s ease forwards' }}>

        {/* ── Header ── */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h1 style={{ fontSize: 28, fontWeight: 800, color: '#f1f5f9', letterSpacing: '-0.02em' }}>
              Grade Review Queue
            </h1>
            <p style={{ color: '#64748b', marginTop: 4, fontSize: 14 }}>
              Review AI-generated grades. Approve accurate ones or override with manual marks.
            </p>
          </div>
          <button
            onClick={() => setShowShortcuts(true)}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '8px 14px', borderRadius: 8,
              border: '1px solid rgba(255,255,255,0.08)',
              background: 'rgba(255,255,255,0.04)',
              color: '#64748b', fontSize: 13, fontFamily: 'Inter, sans-serif',
              cursor: 'pointer', transition: 'all 150ms ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.08)'; e.currentTarget.style.color = '#f1f5f9' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; e.currentTarget.style.color = '#64748b' }}
          >
            <Keyboard size={15} />
            Shortcuts
          </button>
        </div>

        {/* ── Exam Selector ── */}
        <div style={{
          padding: '14px 18px',
          borderRadius: 12,
          background: 'rgba(255,255,255,0.03)',
          border: '1px solid rgba(255,255,255,0.07)',
          display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap',
        }}>
          <p style={{ fontSize: 13, fontWeight: 500, color: '#94a3b8', flexShrink: 0 }}>Select Exam:</p>
          {loadingExams ? (
            <Loader2 size={16} color="#6366f1" style={{ animation: 'spinSlow 0.8s linear infinite' }} />
          ) : (
            <div style={{ position: 'relative', flex: 1, minWidth: 200 }}>
              <select
                value={examId || ''}
                onChange={e => setSearchParams({ exam_id: e.target.value })}
                style={{
                  width: '100%', padding: '8px 36px 8px 12px',
                  borderRadius: 8, border: '1px solid rgba(255,255,255,0.1)',
                  background: 'rgba(255,255,255,0.06)', color: '#f1f5f9',
                  fontSize: 14, fontFamily: 'Inter, sans-serif',
                  appearance: 'none', cursor: 'pointer', outline: 'none',
                }}
              >
                <option value="" style={{ background: '#0d1322' }}>-- Select an exam --</option>
                {exams.map(e => (
                  <option key={e.id} value={e.id} style={{ background: '#0d1322' }}>{e.title}</option>
                ))}
              </select>
              <ChevronDown size={16} color="#475569" style={{
                position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none',
              }} />
            </div>
          )}
        </div>

        {/* ── Progress + Stats ── */}
        {examId && (
          <>
            {/* Overall progress */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <p style={{ fontSize: 12, color: '#64748b', fontWeight: 500 }}>Review Progress</p>
                  <p style={{ fontSize: 12, color: '#818cf8', fontWeight: 700 }}>{donePct}% complete</p>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${donePct}%` }} />
                </div>
              </div>
            </div>

            {/* Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
              {stats.map(stat => (
                <div key={stat.label} style={{
                  padding: '16px 18px', borderRadius: 12,
                  background: stat.bg, border: `1px solid ${stat.border}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                }}>
                  <div>
                    <p style={{ fontSize: 11, color: stat.color, fontWeight: 600, opacity: 0.7 }}>{stat.label}</p>
                    <p style={{ fontSize: 26, fontWeight: 800, color: stat.color, lineHeight: 1.2, marginTop: 2 }}>{stat.value}</p>
                  </div>
                  <stat.icon size={22} color={stat.color} style={{ opacity: 0.5 }} />
                </div>
              ))}
            </div>
          </>
        )}

        {/* ── Main Content ── */}
        {!examId ? (
          <div style={{
            padding: '64px 32px', textAlign: 'center',
            background: 'rgba(255,255,255,0.02)',
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: 16,
          }}>
            <Clock size={48} color="#1e293b" style={{ margin: '0 auto 16px', display: 'block' }} />
            <p style={{ color: '#475569', fontSize: 15 }}>Select an exam above to start reviewing grades.</p>
          </div>
        ) : isLoading ? (
          <div style={{ padding: '64px', textAlign: 'center' }}>
            <div style={{
              width: 44, height: 44, border: '3px solid rgba(99,102,241,0.3)',
              borderTopColor: '#6366f1', borderRadius: '50%',
              animation: 'spinSlow 0.8s linear infinite', margin: '0 auto 16px',
            }} />
            <p style={{ color: '#475569', fontSize: 14 }}>Loading grade queue…</p>
          </div>
        ) : gradeQueue.length > 0 ? (
          <ReviewCard
            grade={currentGrade}
            onApprove={approve}
            onOverride={override}
            onNext={nextGrade}
            onPrevious={previousGrade}
            hasNext={hasNext}
            hasPrev={hasPrev}
            progress={progress}
          />
        ) : (
          <div style={{
            padding: '64px 32px', textAlign: 'center',
            background: 'rgba(16,185,129,0.05)',
            border: '1px solid rgba(16,185,129,0.2)',
            borderRadius: 16,
          }}>
            <CheckCircle size={52} color="#10b981" style={{ margin: '0 auto 16px', display: 'block' }} />
            <h2 style={{ fontSize: 22, fontWeight: 700, color: '#6ee7b7', marginBottom: 8 }}>All Caught Up!</h2>
            <p style={{ color: '#64748b', fontSize: 14 }}>
              There are no pending grades to review for this exam. Great work!
            </p>
          </div>
        )}

        {/* Keyboard shortcuts modal */}
        <KeyboardShortcuts isOpen={showShortcuts} onClose={() => setShowShortcuts(false)} />
      </div>
    </Layout>
  )
}