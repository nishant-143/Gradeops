import React, { useState, useCallback } from 'react'
import {
  CheckCircle, Edit3, ChevronRight, ChevronLeft,
  Brain, AlertTriangle, FileText, TrendingUp,
} from 'lucide-react'
import PlagiarismFlag from './PlagiarismFlag'
import GradeBreakdown from './GradeBreakdown'
import AnswerImagePane from './AnswerImagePane'
import { useToast } from '../../hooks'

function ReviewCard({ grade, onApprove, onOverride, onNext, onPrevious, hasNext, hasPrev, progress }) {
  const toast = useToast()
  const [feedback, setFeedback] = useState('')
  const [isOverriding, setIsOverriding] = useState(false)
  const [overrideMarks, setOverrideMarks] = useState(grade?.marks || 0)
  const [overrideReason, setOverrideReason] = useState('')

  if (!grade) {
    return (
      <div style={{
        padding: '48px 32px', textAlign: 'center',
        background: 'rgba(255,255,255,0.02)',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 16,
      }}>
        <FileText size={40} color="#1e293b" style={{ margin: '0 auto 12px', display: 'block' }} />
        <p style={{ color: '#475569' }}>No submission selected</p>
      </div>
    )
  }

  const handleApprove = useCallback(() => {
    onApprove(feedback)
    setFeedback('')
  }, [feedback, onApprove])

  const handleOverride = useCallback(() => {
    if (overrideMarks === '' || overrideReason.trim() === '') {
      toast.error('Please fill in marks and reason')
      return
    }
    onOverride(parseFloat(overrideMarks), overrideReason)
    setIsOverriding(false)
    setOverrideMarks(grade.marks)
    setOverrideReason('')
  }, [overrideMarks, overrideReason, onOverride, grade.marks, toast])

  /* Confidence radial */
  const confidence = grade.confidence_score ?? null
  const confPct = confidence !== null ? Math.round(confidence * 100) : null
  const confColor = confPct >= 80 ? '#10b981' : confPct >= 60 ? '#f59e0b' : '#ef4444'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20, animation: 'slideUp 0.3s ease forwards' }}>

      {/* ── Top bar: student info + progress ── */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        flexWrap: 'wrap', gap: 12,
        padding: '14px 20px',
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.07)',
        borderRadius: 12,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {/* Student avatar */}
          <div style={{
            width: 38, height: 38, borderRadius: '50%',
            background: 'linear-gradient(135deg,#6366f1,#8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 15, fontWeight: 700, color: '#fff',
          }}>
            {(grade.student_name || grade.student_id || 'S')[0].toUpperCase()}
          </div>
          <div>
            <p style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0' }}>
              {grade.student_name || grade.student_id || 'Unknown Student'}
            </p>
            {grade.student_id && grade.student_name && (
              <p style={{ fontSize: 12, color: '#475569' }}>ID: {grade.student_id}</p>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          {/* Confidence indicator */}
          {confPct !== null && (
            <div style={{ textAlign: 'center' }}>
              <div style={{ position: 'relative', width: 44, height: 44, margin: '0 auto' }}>
                <svg width="44" height="44" style={{ transform: 'rotate(-90deg)' }}>
                  <circle cx="22" cy="22" r="18" fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="4" />
                  <circle cx="22" cy="22" r="18" fill="none" stroke={confColor} strokeWidth="4"
                    strokeDasharray={`${2 * Math.PI * 18}`}
                    strokeDashoffset={`${2 * Math.PI * 18 * (1 - confidence)}`}
                    strokeLinecap="round"
                    style={{ transition: 'stroke-dashoffset 0.5s ease' }}
                  />
                </svg>
                <span style={{
                  position: 'absolute', inset: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 11, fontWeight: 700, color: confColor,
                }}>
                  {confPct}%
                </span>
              </div>
              <p style={{ fontSize: 10, color: '#475569', marginTop: 3, fontWeight: 600 }}>AI Conf.</p>
            </div>
          )}

          {/* Progress */}
          <div style={{ textAlign: 'right' }}>
            <p style={{ fontSize: 13, fontWeight: 700, color: '#818cf8' }}>{progress}</p>
            <p style={{ fontSize: 11, color: '#475569' }}>in queue</p>
          </div>
        </div>
      </div>

      {/* ── Main split panel ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 20, alignItems: 'start' }}>

        {/* Left: Answer image pane */}
        <AnswerImagePane grade={grade} />

        {/* Right column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

          {/* AI Grade breakdown */}
          <GradeBreakdown grade={grade} />

          {/* Plagiarism flag */}
          {grade.plagiarism_score && <PlagiarismFlag grade={grade} />}

          {/* ── Actions panel ── */}
          <div style={{
            padding: 20,
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(255,255,255,0.07)',
            borderRadius: 14,
          }}>
            {!isOverriding ? (
              <>
                <p style={{ fontSize: 12, fontWeight: 700, color: '#475569', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 12 }}>
                  TA Decision
                </p>

                {/* Feedback input */}
                <div style={{ marginBottom: 12 }}>
                  <label className="label">Feedback for Student <span style={{ color: '#334155', fontWeight: 400 }}>(optional)</span></label>
                  <textarea
                    className="input textarea"
                    value={feedback}
                    onChange={e => setFeedback(e.target.value)}
                    placeholder="Add feedback or comments for the student…"
                    rows={3}
                  />
                </div>

                {/* Approve button */}
                <button
                  onClick={handleApprove}
                  className="btn btn-success btn-full"
                  style={{ marginBottom: 8 }}
                >
                  <CheckCircle size={17} />
                  Approve Grade
                  <span style={{
                    marginLeft: 'auto', padding: '2px 7px', borderRadius: 5,
                    background: 'rgba(255,255,255,0.15)',
                    fontSize: 11, fontWeight: 700, letterSpacing: '0.04em',
                  }}>Enter</span>
                </button>

                {/* Override button */}
                <button
                  onClick={() => { setIsOverriding(true); setOverrideMarks(grade.marks) }}
                  className="btn btn-warning btn-full"
                >
                  <Edit3 size={17} />
                  Override Grade
                  <span style={{
                    marginLeft: 'auto', padding: '2px 7px', borderRadius: 5,
                    background: 'rgba(0,0,0,0.12)',
                    fontSize: 11, fontWeight: 700, letterSpacing: '0.04em',
                  }}>O</span>
                </button>
              </>
            ) : (
              <>
                <p style={{ fontSize: 12, fontWeight: 700, color: '#fcd34d', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 12 }}>
                  ✏️ Override Grade
                </p>

                <div style={{ marginBottom: 12 }}>
                  <label className="label">New Marks</label>
                  <input
                    type="number"
                    className="input"
                    value={overrideMarks}
                    onChange={e => setOverrideMarks(e.target.value)}
                    placeholder="Enter new marks"
                    min="0"
                  />
                </div>

                <div style={{ marginBottom: 14 }}>
                  <label className="label">Reason for Override *</label>
                  <textarea
                    className="input textarea"
                    value={overrideReason}
                    onChange={e => setOverrideReason(e.target.value)}
                    placeholder="Explain why you're changing the AI grade…"
                    rows={3}
                  />
                </div>

                <button onClick={handleOverride} className="btn btn-warning btn-full" style={{ marginBottom: 8 }}>
                  Confirm Override
                </button>
                <button
                  onClick={() => { setIsOverriding(false); setOverrideReason('') }}
                  className="btn btn-ghost btn-full"
                >
                  Cancel
                </button>
              </>
            )}
          </div>

          {/* ── Navigation ── */}
          <div style={{ display: 'flex', gap: 10 }}>
            <button
              onClick={onPrevious}
              disabled={!hasPrev}
              className="btn btn-ghost"
              style={{ flex: 1 }}
            >
              <ChevronLeft size={16} />
              Previous
              <span style={{ marginLeft: 'auto', fontSize: 11, padding: '1px 6px', borderRadius: 4, background: 'rgba(255,255,255,0.08)' }}>K</span>
            </button>
            <button
              onClick={onNext}
              disabled={!hasNext}
              className="btn btn-primary"
              style={{ flex: 1 }}
            >
              Next
              <ChevronRight size={16} />
              <span style={{ marginLeft: 'auto', fontSize: 11, padding: '1px 6px', borderRadius: 4, background: 'rgba(255,255,255,0.15)' }}>J</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default React.memo(ReviewCard, (prev, next) =>
  prev.grade?.id === next.grade?.id &&
  prev.progress === next.progress &&
  prev.hasNext === next.hasNext &&
  prev.hasPrev === next.hasPrev
)
