import React, { useEffect } from 'react'
import { Keyboard, X } from 'lucide-react'

const SHORTCUTS = [
  { key: '?',     action: 'Show this help'    },
  { key: 'j',     action: 'Next submission'   },
  { key: 'k',     action: 'Previous submission'},
  { key: 'Enter', action: 'Approve grade'     },
  { key: 'o',     action: 'Override grade'    },
  { key: 'Esc',   action: 'Close modal'       },
]

/**
 * KeyboardShortcuts — controlled modal (accepts isOpen/onClose props)
 * Also listens to '?' key to toggle, and Escape to close
 */
function KeyboardShortcuts({ isOpen, onClose }) {
  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'Escape' && isOpen) onClose()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div
      style={{
        position: 'fixed', inset: 0, zIndex: 100,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'rgba(0,0,0,0.6)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        animation: 'fadeIn 200ms ease',
      }}
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div style={{
        width: '100%', maxWidth: 420,
        margin: 16,
        background: 'rgba(13,19,34,0.96)',
        backdropFilter: 'blur(32px)',
        WebkitBackdropFilter: 'blur(32px)',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: 20,
        boxShadow: '0 24px 64px rgba(0,0,0,0.5)',
        animation: 'slideUp 0.25s ease',
        overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{
          padding: '18px 20px',
          borderBottom: '1px solid rgba(255,255,255,0.07)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: 'rgba(99,102,241,0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Keyboard size={16} color="#818cf8" />
            </div>
            <p style={{ fontSize: 15, fontWeight: 700, color: '#f1f5f9' }}>Keyboard Shortcuts</p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'rgba(255,255,255,0.06)', border: 'none',
              borderRadius: 7, cursor: 'pointer', color: '#64748b',
              width: 30, height: 30, display: 'flex', alignItems: 'center', justifyContent: 'center',
              transition: 'all 150ms ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.12)'; e.currentTarget.style.color = '#f1f5f9' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.06)'; e.currentTarget.style.color = '#64748b' }}
          >
            <X size={15} />
          </button>
        </div>

        {/* Shortcuts list */}
        <div style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 8 }}>
          {SHORTCUTS.map((s, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '10px 12px', borderRadius: 8,
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.05)',
            }}>
              <p style={{ fontSize: 13, color: '#94a3b8' }}>{s.action}</p>
              <kbd style={{
                padding: '3px 10px', borderRadius: 6,
                background: 'rgba(99,102,241,0.1)',
                border: '1px solid rgba(99,102,241,0.25)',
                color: '#a5b4fc', fontSize: 12, fontFamily: 'Inter, monospace',
                fontWeight: 600, letterSpacing: '0.03em',
              }}>
                {s.key}
              </kbd>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div style={{
          padding: '12px 20px',
          borderTop: '1px solid rgba(255,255,255,0.06)',
          display: 'flex', justifyContent: 'flex-end',
        }}>
          <button onClick={onClose} className="btn btn-ghost btn-sm">
            Close (Esc)
          </button>
        </div>
      </div>
    </div>
  )
}

export default React.memo(KeyboardShortcuts)
