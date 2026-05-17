import React from 'react'
import { TrendingUp, Brain } from 'lucide-react'

const COLORS = ['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444']

function GradeBreakdown({ grade }) {
  if (!grade?.criteria_marks) return null

  const criteriaMarks = Array.isArray(grade.criteria_marks) ? grade.criteria_marks : []
  const totalMarks = grade.total_marks || criteriaMarks.reduce((s, c) => s + (c.max_marks || 0), 0)
  const pct = totalMarks > 0 ? ((grade.marks || 0) / totalMarks * 100).toFixed(1) : 0

  const getGradeLetter = (p) => {
    if (p >= 90) return 'A'
    if (p >= 80) return 'B'
    if (p >= 70) return 'C'
    if (p >= 60) return 'D'
    return 'F'
  }

  const gradeColor = pct >= 80 ? '#10b981' : pct >= 60 ? '#818cf8' : pct >= 40 ? '#f59e0b' : '#ef4444'

  return (
    <div style={{
      padding: 20,
      background: 'rgba(255,255,255,0.03)',
      border: '1px solid rgba(255,255,255,0.07)',
      borderRadius: 14,
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
        <Brain size={16} color="#818cf8" />
        <p style={{ fontSize: 12, fontWeight: 700, color: '#475569', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
          AI Grade Breakdown
        </p>
      </div>

      {/* Overall score */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 14, marginBottom: 18,
        padding: '14px 16px', borderRadius: 10,
        background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)',
      }}>
        <div style={{
          width: 52, height: 52, borderRadius: 12, flexShrink: 0,
          background: `${gradeColor}15`,
          border: `1px solid ${gradeColor}25`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 22, fontWeight: 900, color: gradeColor,
        }}>
          {getGradeLetter(pct)}
        </div>
        <div>
          <p style={{ fontSize: 22, fontWeight: 800, color: '#f1f5f9', lineHeight: 1 }}>
            {grade.marks} <span style={{ fontSize: 14, fontWeight: 400, color: '#475569' }}>/ {totalMarks}</span>
          </p>
          <p style={{ fontSize: 13, color: '#64748b', marginTop: 3 }}>{pct}% — AI Assessed</p>
        </div>
      </div>

      {/* Per-criterion bars */}
      {criteriaMarks.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {criteriaMarks.map((criterion, i) => {
            const barPct = criterion.max_marks > 0
              ? Math.min((criterion.marks / criterion.max_marks) * 100, 100)
              : 0
            return (
              <div key={i}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 5 }}>
                  <p style={{ fontSize: 13, color: '#94a3b8', fontWeight: 500 }}>
                    {criterion.name || `Criterion ${i + 1}`}
                  </p>
                  <p style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0' }}>
                    {criterion.marks}<span style={{ color: '#475569', fontWeight: 400 }}>/{criterion.max_marks}</span>
                  </p>
                </div>
                <div style={{
                  height: 6, borderRadius: 3, overflow: 'hidden',
                  background: 'rgba(255,255,255,0.06)',
                }}>
                  <div style={{
                    width: `${barPct}%`, height: '100%',
                    background: `linear-gradient(90deg, ${COLORS[i % COLORS.length]}, ${COLORS[i % COLORS.length]}bb)`,
                    borderRadius: 3,
                    transition: 'width 0.5s ease',
                  }} />
                </div>
                {/* AI justification text */}
                {criterion.justification && (
                  <p style={{
                    fontSize: 11, color: '#475569',
                    marginTop: 4, lineHeight: 1.5,
                    padding: '6px 8px',
                    background: 'rgba(255,255,255,0.02)',
                    borderRadius: 6,
                    borderLeft: `2px solid ${COLORS[i % COLORS.length]}40`,
                  }}>
                    {criterion.justification}
                  </p>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Overall AI feedback */}
      {grade.feedback && (
        <div style={{
          marginTop: 14, padding: '10px 12px', borderRadius: 8,
          background: 'rgba(99,102,241,0.07)',
          border: '1px solid rgba(99,102,241,0.15)',
        }}>
          <p style={{ fontSize: 11, fontWeight: 700, color: '#818cf8', marginBottom: 4, letterSpacing: '0.04em' }}>
            AI FEEDBACK
          </p>
          <p style={{ fontSize: 12, color: '#94a3b8', lineHeight: 1.6 }}>{grade.feedback}</p>
        </div>
      )}
    </div>
  )
}

export default React.memo(GradeBreakdown)
