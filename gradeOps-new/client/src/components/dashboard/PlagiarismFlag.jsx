import React from 'react'
import { AlertTriangle, ShieldAlert } from 'lucide-react'

function PlagiarismFlag({ grade }) {
  if (!grade?.plagiarism_score) return null

  const score = grade.plagiarism_score
  const pct = Math.round(score * 100)

  const level = score > 0.8 ? 'critical' : score > 0.7 ? 'high' : score > 0.5 ? 'medium' : 'low'
  const config = {
    critical: { label: 'Critical Risk',  color: '#ef4444', bg: 'rgba(239,68,68,0.08)',  border: 'rgba(239,68,68,0.2)',  bar: '#ef4444' },
    high:     { label: 'High Risk',      color: '#f97316', bg: 'rgba(249,115,22,0.08)', border: 'rgba(249,115,22,0.2)', bar: '#f97316' },
    medium:   { label: 'Medium Risk',    color: '#f59e0b', bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.2)', bar: '#f59e0b' },
    low:      { label: 'Low Risk',       color: '#10b981', bg: 'rgba(16,185,129,0.08)', border: 'rgba(16,185,129,0.2)', bar: '#10b981' },
  }[level]

  return (
    <div style={{
      padding: '14px 16px',
      borderRadius: 12,
      background: config.bg,
      border: `1px solid ${config.border}`,
    }}>
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <ShieldAlert size={16} color={config.color} />
          <p style={{ fontSize: 13, fontWeight: 700, color: config.color }}>Plagiarism Detection</p>
        </div>
        <span style={{
          padding: '2px 9px', borderRadius: 9999,
          background: `${config.color}20`, border: `1px solid ${config.color}30`,
          fontSize: 11, fontWeight: 700, color: config.color,
          letterSpacing: '0.04em',
        }}>
          {config.label}
        </span>
      </div>

      {/* Progress bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          flex: 1, height: 6, borderRadius: 3,
          background: 'rgba(255,255,255,0.08)', overflow: 'hidden',
        }}>
          <div style={{
            width: `${Math.min(pct, 100)}%`, height: '100%',
            background: config.bar, borderRadius: 3,
            transition: 'width 0.5s ease',
          }} />
        </div>
        <p style={{ fontSize: 13, fontWeight: 800, color: config.color, flexShrink: 0 }}>{pct}%</p>
      </div>

      {/* Warning text */}
      {score > 0.7 && (
        <p style={{ fontSize: 12, color: config.color, marginTop: 8, opacity: 0.8, lineHeight: 1.5 }}>
          ⚠️ This submission shows high similarity to other answers. Review carefully before approving.
        </p>
      )}

      {grade.similar_to && (
        <p style={{ fontSize: 11, color: '#64748b', marginTop: 6 }}>
          Similar to: {grade.similar_to}
        </p>
      )}
    </div>
  )
}

export default React.memo(PlagiarismFlag)
