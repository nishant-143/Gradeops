import React, { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import {
  Plus, BarChart3, FileText, Clock, Upload, BookOpen,
  Cpu, ClipboardCheck, Download, TrendingUp, Trash2, ArrowRight,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { examsAPI } from '../api'
import { useToast } from '../hooks'
import { useAuthStore } from '../store/authStore'

const STATUS = {
  draft:      { label: 'Draft',      color: 'var(--color-text-muted)', bg: 'var(--color-surface-hover)', border: 'var(--color-border)' },
  processing: { label: 'Processing', color: 'var(--color-info)',        bg: 'var(--color-info-bg)',        border: 'rgba(56,189,248,0.3)' },
  ready:      { label: 'In Review',  color: 'var(--color-warning)',     bg: 'var(--color-warning-bg)',     border: 'rgba(245,158,11,0.3)' },
  complete:   { label: 'Complete',   color: 'var(--color-success)',     bg: 'var(--color-success-bg)',     border: 'rgba(34,197,94,0.3)'  },
}

const PIPELINE = [
  { icon: Upload,         label: 'Publish',   color: '#14b8a6' },
  { icon: BookOpen,       label: 'Rubric',    color: '#a78bfa' },
  { icon: Cpu,            label: 'AI Grade',  color: '#38bdf8' },
  { icon: ClipboardCheck, label: 'Review',    color: '#fbbf24' },
  { icon: Download,       label: 'Export',    color: '#34d399' },
]

const MOCK = [
  { id: '1', title: 'Midterm Exam – CS101', status: 'ready',      submissions: 45, graded: 32, created_at: '2024-04-15' },
  { id: '2', title: 'Final Exam – CS101',   status: 'processing', submissions: 48, graded: 12, created_at: '2024-04-20' },
  { id: '3', title: 'Quiz 3 – CS201',       status: 'complete',   submissions: 30, graded: 30, created_at: '2024-04-10' },
]

export default function InstructorDashboard() {
  const navigate = useNavigate()
  const toast    = useToast()
  const { user } = useAuthStore()
  const [exams, setExams]       = useState(MOCK)
  const [loading, setLoading]   = useState(false)

  useEffect(() => { load() }, [])

  const load = async () => {
    setLoading(true)
    try {
      const d = await examsAPI.listExams()
      setExams(d?.exams?.length > 0 ? d.exams : [])
    } catch {} finally { setLoading(false) }
  }

  const del = async (id) => {
    if (!window.confirm('Delete this exam and all its data?')) return
    try { await examsAPI.deleteExam(id); toast.success('Deleted'); load() }
    catch { toast.error('Failed to delete') }
  }

  const totalSubs    = exams.reduce((s, e) => s + (e.submissions || 0), 0)
  const totalGraded  = exams.reduce((s, e) => s + (e.graded || 0), 0)
  const pending      = exams.filter(e => e.status === 'ready').reduce((s, e) => s + ((e.submissions || 0) - (e.graded || 0)), 0)

  const stats = [
    { label: 'Exams',       value: exams.length,     icon: FileText,   color: '#14b8a6' },
    { label: 'Pending',     value: pending || 0,     icon: Clock,      color: '#f59e0b' },
    { label: 'Submissions', value: totalSubs || 0,   icon: BarChart3,  color: '#38bdf8' },
    { label: 'Graded',      value: totalGraded || 0, icon: TrendingUp, color: '#22c55e' },
  ]

  return (
    <Layout>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 22, animation: 'slideUp 0.25s ease forwards' }}>

        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 700, color: 'var(--color-text)', letterSpacing: '-0.02em' }}>
              Dashboard
            </h1>
            <p style={{ fontSize: 13, color: 'var(--color-text-muted)', marginTop: 2 }}>
              Welcome back{user?.email ? `, ${user.email.split('@')[0]}` : ''}
            </p>
          </div>
          <button onClick={() => navigate('/upload')} className="btn btn-primary">
            <Plus size={15} /> New Exam
          </button>
        </div>

        {/* Stats row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px,1fr))', gap: 12 }}>
          {stats.map((s, i) => (
            <div key={s.label} className="stat-card" style={{ animation: `slideUp 0.25s ease ${i*0.05}s forwards`, opacity: 0 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                <span style={{ fontSize: 12, color: 'var(--color-text-muted)', fontWeight: 500 }}>{s.label}</span>
                <div style={{ width: 30, height: 30, borderRadius: 8, background: `${s.color}18`, border: `1px solid ${s.color}28`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <s.icon size={14} color={s.color} />
                </div>
              </div>
              <p style={{ fontSize: 30, fontWeight: 700, color: 'var(--color-text)', lineHeight: 1 }}>{s.value}</p>
            </div>
          ))}
        </div>

        {/* Pipeline strip */}
        <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', padding: '14px 20px' }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: 'var(--color-text-faint)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 14 }}>Grading Pipeline</p>
          <div style={{ display: 'flex', alignItems: 'center', gap: 0 }}>
            {PIPELINE.map((p, i) => (
              <React.Fragment key={p.label}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 7, flex: 1 }}>
                  <div style={{ width: 36, height: 36, borderRadius: 9, background: `${p.color}18`, border: `1px solid ${p.color}30`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <p.icon size={16} color={p.color} />
                  </div>
                  <span style={{ fontSize: 11, color: 'var(--color-text-muted)', fontWeight: 500 }}>{p.label}</span>
                </div>
                {i < PIPELINE.length - 1 && (
                  <ArrowRight size={13} color="var(--color-text-faint)" style={{ flexShrink: 0, margin: '0 4px', marginBottom: 16 }} />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Exams table */}
        <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
          <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--color-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h2 style={{ fontSize: 14, fontWeight: 600, color: 'var(--color-text)' }}>Your Exams</h2>
            <button onClick={() => navigate('/upload')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-primary)', fontSize: 12, fontWeight: 500, display: 'flex', alignItems: 'center', gap: 4, fontFamily: 'Inter, sans-serif' }}>
              <Plus size={13} /> Add
            </button>
          </div>

          {loading ? (
            <div style={{ padding: 48, textAlign: 'center', color: 'var(--color-text-faint)' }}>
              <div style={{ width: 28, height: 28, border: '2px solid var(--color-border)', borderTopColor: 'var(--color-primary)', borderRadius: '50%', animation: 'spinSlow 0.8s linear infinite', margin: '0 auto 10px' }} />
              <p style={{ fontSize: 13 }}>Loading…</p>
            </div>
          ) : exams.length === 0 ? (
            <div style={{ padding: '56px 24px', textAlign: 'center' }}>
              <FileText size={36} color="var(--color-border-hover)" style={{ margin: '0 auto 12px', display: 'block' }} />
              <p style={{ color: 'var(--color-text-muted)', fontSize: 13, marginBottom: 14 }}>No exams yet. Create your first one.</p>
              <button onClick={() => navigate('/upload')} className="btn btn-primary btn-sm"><Plus size={13} /> Create Exam</button>
            </div>
          ) : (
            <>
              {/* Col headers */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 100px 140px 110px auto', padding: '8px 20px', borderBottom: '1px solid var(--color-border)' }}>
                {['Exam', 'Subs', 'Graded', 'Status', 'Actions'].map(h => (
                  <p key={h} style={{ fontSize: 11, fontWeight: 600, color: 'var(--color-text-faint)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{h}</p>
                ))}
              </div>

              {exams.map((exam, i) => {
                const cfg = STATUS[exam.status] || STATUS.draft
                const pct = exam.submissions > 0 ? Math.round((exam.graded / exam.submissions) * 100) : 0
                return (
                  <div key={exam.id} style={{
                    display: 'grid', gridTemplateColumns: '1fr 100px 140px 110px auto',
                    padding: '13px 20px', alignItems: 'center',
                    borderBottom: i < exams.length - 1 ? '1px solid var(--color-border)' : 'none',
                    transition: 'background 120ms ease',
                    animation: `slideUp 0.2s ease ${i*0.05}s forwards`, opacity: 0,
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--color-surface-hover)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                  >
                    <div>
                      <p style={{ fontSize: 13, fontWeight: 500, color: 'var(--color-text)' }}>{exam.title}</p>
                      <p style={{ fontSize: 11, color: 'var(--color-text-faint)', marginTop: 2 }}>{new Date(exam.created_at).toLocaleDateString()}</p>
                    </div>

                    <p style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>{exam.submissions || 0}</p>

                    <div>
                      <p style={{ fontSize: 12, color: 'var(--color-text-muted)', marginBottom: 4 }}>{exam.graded || 0} / {exam.submissions || 0}</p>
                      <div style={{ width: 80, height: 3, background: 'var(--color-border)', borderRadius: 2, overflow: 'hidden' }}>
                        <div style={{ width: `${pct}%`, height: '100%', background: 'var(--color-primary)', borderRadius: 2 }} />
                      </div>
                    </div>

                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '3px 8px', borderRadius: 99, background: cfg.bg, border: `1px solid ${cfg.border}`, color: cfg.color, fontSize: 11, fontWeight: 600 }}>
                      {exam.status === 'processing' && <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'currentColor', display: 'inline-block', animation: 'pulseDot 1.5s ease-in-out infinite' }} />}
                      {cfg.label}
                    </span>

                    <div style={{ display: 'flex', gap: 4 }}>
                      {[
                        { label: 'Upload', path: `/upload/${exam.id}`, c: '#38bdf8' },
                        { label: 'Rubric', path: `/rubric/${exam.id}`, c: '#a78bfa' },
                        { label: 'Export', path: `/export/${exam.id}`, c: '#34d399' },
                      ].map(a => (
                        <button key={a.label} onClick={() => navigate(a.path)} style={{
                          padding: '3px 9px', borderRadius: 5,
                          background: `${a.c}14`, border: `1px solid ${a.c}28`,
                          color: a.c, fontSize: 11, fontWeight: 500,
                          cursor: 'pointer', fontFamily: 'Inter, sans-serif', transition: 'all 120ms ease',
                        }}
                        onMouseEnter={e => e.currentTarget.style.background = `${a.c}24`}
                        onMouseLeave={e => e.currentTarget.style.background = `${a.c}14`}
                        >{a.label}</button>
                      ))}
                      <button onClick={() => del(exam.id)} style={{ padding: '3px 7px', borderRadius: 5, background: 'var(--color-danger-bg)', border: '1px solid rgba(244,63,94,0.22)', color: 'var(--color-danger)', cursor: 'pointer', display: 'flex', alignItems: 'center', transition: 'opacity 120ms ease' }}
                        onMouseEnter={e => e.currentTarget.style.opacity = '0.7'}
                        onMouseLeave={e => e.currentTarget.style.opacity = '1'}
                        title="Delete">
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </div>
                )
              })}
            </>
          )}
        </div>
      </div>
    </Layout>
  )
}
