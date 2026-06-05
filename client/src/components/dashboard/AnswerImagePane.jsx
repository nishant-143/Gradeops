import React, { useState } from 'react'
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, FileText, AlignLeft } from 'lucide-react'

/**
 * AnswerImagePane — Shows OCR'd text + cropped answer image side by side
 * Falls back gracefully when no images or OCR text is available
 */
function AnswerImagePane({ grade }) {
  const [currentPage, setCurrentPage] = useState(0)
  const [zoom, setZoom] = useState(100)
  const [activeTab, setActiveTab] = useState('image') // 'image' | 'ocr'

  const hasImages = grade?.answer_images?.length > 0
  const hasOcr    = !!grade?.ocr_text

  if (!hasImages && !hasOcr) {
    return (
      <div style={{
        padding: '48px 24px', textAlign: 'center',
        background: 'rgba(255,255,255,0.02)',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 14,
        minHeight: 320,
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12,
      }}>
        <FileText size={40} color="#1e293b" />
        <p style={{ color: '#475569', fontSize: 14 }}>No answer content available</p>
        <p style={{ color: '#334155', fontSize: 12 }}>Images will appear here after OCR processing</p>
      </div>
    )
  }

  const images = grade?.answer_images || []
  const currentImage = images[currentPage]

  const Tab = ({ id, icon: Icon, label }) => (
    <button
      onClick={() => setActiveTab(id)}
      style={{
        padding: '7px 16px', borderRadius: 8, border: 'none',
        cursor: 'pointer', fontFamily: 'Inter, sans-serif',
        fontSize: 13, fontWeight: 600,
        display: 'flex', alignItems: 'center', gap: 6,
        background: activeTab === id ? 'rgba(99,102,241,0.15)' : 'transparent',
        color: activeTab === id ? '#818cf8' : '#475569',
        transition: 'all 150ms ease',
      }}
    >
      <Icon size={15} />
      {label}
    </button>
  )

  return (
    <div style={{
      borderRadius: 14, overflow: 'hidden',
      background: 'rgba(255,255,255,0.02)',
      border: '1px solid rgba(255,255,255,0.07)',
      display: 'flex', flexDirection: 'column',
      minHeight: 500,
    }}>
      {/* ── Toolbar ── */}
      <div style={{
        padding: '10px 16px',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        background: 'rgba(255,255,255,0.02)',
        flexWrap: 'wrap', gap: 8,
      }}>
        {/* Tabs */}
        <div style={{ display: 'flex', gap: 2 }}>
          {hasImages && <Tab id="image" icon={FileText} label="Answer Image" />}
          {hasOcr    && <Tab id="ocr"   icon={AlignLeft} label="OCR Text" />}
        </div>

        {/* Zoom controls (image only) */}
        {activeTab === 'image' && hasImages && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <button
              onClick={() => setZoom(z => Math.max(50, z - 10))}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#475569', padding: 6, display: 'flex', borderRadius: 6, transition: 'all 150ms' }}
              onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.06)'}
              onMouseLeave={e => e.currentTarget.style.background = 'none'}
            >
              <ZoomOut size={15} />
            </button>
            <span style={{ fontSize: 12, color: '#64748b', fontWeight: 500, minWidth: 44, textAlign: 'center' }}>
              {zoom}%
            </span>
            <button
              onClick={() => setZoom(z => Math.min(200, z + 10))}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#475569', padding: 6, display: 'flex', borderRadius: 6, transition: 'all 150ms' }}
              onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.06)'}
              onMouseLeave={e => e.currentTarget.style.background = 'none'}
            >
              <ZoomIn size={15} />
            </button>
          </div>
        )}

        {/* Page count */}
        {activeTab === 'image' && images.length > 1 && (
          <p style={{ fontSize: 12, color: '#475569' }}>
            Page {currentPage + 1} / {images.length}
          </p>
        )}
      </div>

      {/* ── Content ── */}
      <div style={{ flex: 1, overflow: 'auto', position: 'relative' }}>

        {/* Image view */}
        {activeTab === 'image' && (
          <div style={{
            minHeight: 420, display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: 'rgba(0,0,0,0.2)', padding: 16,
          }}>
            {currentImage ? (
              <img
                src={currentImage}
                alt={`Answer page ${currentPage + 1}`}
                style={{
                  maxWidth: '100%', borderRadius: 8,
                  transform: `scale(${zoom / 100})`,
                  transformOrigin: 'center top',
                  transition: 'transform 200ms ease',
                  boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
                }}
              />
            ) : (
              <div style={{ textAlign: 'center', color: '#334155' }}>
                <FileText size={32} style={{ margin: '0 auto 8px', display: 'block', opacity: 0.4 }} />
                <p style={{ fontSize: 13 }}>Image loading…</p>
              </div>
            )}
          </div>
        )}

        {/* OCR text view */}
        {activeTab === 'ocr' && (
          <div style={{ padding: 20 }}>
            <div style={{
              padding: '4px 10px', borderRadius: 6, marginBottom: 12,
              background: 'rgba(59,130,246,0.08)', border: '1px solid rgba(59,130,246,0.15)',
              display: 'inline-flex', alignItems: 'center', gap: 6,
            }}>
              <AlignLeft size={12} color="#60a5fa" />
              <p style={{ fontSize: 11, color: '#60a5fa', fontWeight: 600 }}>Extracted by Qwen-VL OCR</p>
            </div>
            <pre style={{
              fontFamily: 'Inter, monospace',
              fontSize: 13, lineHeight: 1.8,
              color: '#94a3b8',
              whiteSpace: 'pre-wrap', wordBreak: 'break-word',
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid rgba(255,255,255,0.05)',
              borderRadius: 10,
              padding: '14px 16px',
              margin: 0,
            }}>
              {grade.ocr_text || 'No OCR text available.'}
            </pre>
          </div>
        )}
      </div>

      {/* ── Page navigation ── */}
      {activeTab === 'image' && images.length > 1 && (
        <div style={{
          padding: '10px 16px',
          borderTop: '1px solid rgba(255,255,255,0.06)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          background: 'rgba(255,255,255,0.02)',
        }}>
          <button
            onClick={() => setCurrentPage(p => Math.max(0, p - 1))}
            disabled={currentPage === 0}
            style={{
              background: 'none', border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 7, padding: '5px 10px', cursor: 'pointer',
              color: currentPage === 0 ? '#334155' : '#94a3b8',
              display: 'flex', alignItems: 'center', gap: 4, fontSize: 12,
              fontFamily: 'Inter, sans-serif', transition: 'all 150ms',
            }}
          >
            <ChevronLeft size={15} /> Prev
          </button>

          {/* Dot indicators */}
          <div style={{ display: 'flex', gap: 6 }}>
            {images.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentPage(i)}
                style={{
                  width: i === currentPage ? 18 : 7,
                  height: 7, borderRadius: 4, border: 'none', cursor: 'pointer',
                  background: i === currentPage
                    ? 'linear-gradient(90deg,#6366f1,#818cf8)'
                    : 'rgba(255,255,255,0.15)',
                  transition: 'all 300ms ease',
                  padding: 0,
                }}
                title={`Page ${i + 1}`}
              />
            ))}
          </div>

          <button
            onClick={() => setCurrentPage(p => Math.min(images.length - 1, p + 1))}
            disabled={currentPage === images.length - 1}
            style={{
              background: 'none', border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 7, padding: '5px 10px', cursor: 'pointer',
              color: currentPage === images.length - 1 ? '#334155' : '#94a3b8',
              display: 'flex', alignItems: 'center', gap: 4, fontSize: 12,
              fontFamily: 'Inter, sans-serif', transition: 'all 150ms',
            }}
          >
            Next <ChevronRight size={15} />
          </button>
        </div>
      )}
    </div>
  )
}

export default React.memo(AnswerImagePane)
