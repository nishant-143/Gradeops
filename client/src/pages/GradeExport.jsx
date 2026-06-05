import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import {
  Download, FileText, AlertCircle, CheckCircle2, Loader2,
  FileSpreadsheet, FileJson, Filter, ChevronDown, Upload,
  Clock, BarChart3, Users, BookOpen, ArrowRight, RefreshCw, Cpu
} from 'lucide-react'
import { examsAPI, submissionsAPI, rubricsAPI, systemAPI, pipelineAPI } from '../api'
import { useToast } from '../hooks'

const STATUS_BADGES = {
  uploaded:   { label: 'Uploaded',   bg: 'rgba(59,130,246,0.1)',  border: 'rgba(59,130,246,0.2)',  color: '#93c5fd' },
  processing: { label: 'Processing', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.2)', color: '#fcd34d' },
  graded:     { label: 'Graded',     bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.2)', color: '#6ee7b7' },
  error:      { label: 'Error',      bg: 'rgba(239,68,68,0.1)',  border: 'rgba(239,68,68,0.2)',  color: '#fca5a5' },
}

export default function GradeExport() {
  const { examId: paramExamId } = useParams()
  const navigate = useNavigate()
  const toast = useToast()

  const [exams, setExams] = useState([])
  const [selectedExamId, setSelectedExamId] = useState(paramExamId || '')
  const [submissions, setSubmissions] = useState([])
  const [rubric, setRubric] = useState(null)
  const [examSummary, setExamSummary] = useState(null)
  
  const [ocrRunning, setOcrRunning] = useState(false)
  const [llmConfigured, setLlmConfigured] = useState(false)
  const [pipelineTriggered, setPipelineTriggered] = useState(false)
  const [isTriggering, setIsTriggering] = useState(false)

  const handleTriggerPipeline = async () => {
    if (submissions.length === 0) return
    setIsTriggering(true)
    try {
      await Promise.all(
        submissions.map(sub => pipelineAPI.trigger(sub.id))
      )
      toast.success('AI grading pipeline triggered for all submissions!')
      await loadExamDetails(selectedExamId)
    } catch (err) {
      toast.error('Failed to trigger pipeline')
    } finally {
      setIsTriggering(false)
    }
  }

  const [format, setFormat] = useState('csv')
  const [includeJustification, setIncludeJustification] = useState(true)
  const [includePlagiarism, setIncludePlagiarism] = useState(true)
  const [isExporting, setIsExporting] = useState(false)
  const [isLoadingExams, setIsLoadingExams] = useState(true)
  const [isLoadingDetails, setIsLoadingDetails] = useState(false)

  useEffect(() => { loadExams() }, [])

  useEffect(() => {
    if (selectedExamId) loadExamDetails(selectedExamId)
  }, [selectedExamId])

  const loadExams = async () => {
    try {
      const data = await examsAPI.listExams()
      const list = data.exams || []
      setExams(list)
      if (!selectedExamId && list.length > 0) setSelectedExamId(list[0].id)
    } catch {
      toast.error('Failed to load exams')
    } finally { setIsLoadingExams(false) }
  }

  const loadExamDetails = async (examId) => {
    setIsLoadingDetails(true)
    try {
      const [subsData, rubricData, summaryData, healthData, pipelineData] = await Promise.allSettled([
        submissionsAPI.listSubmissions(examId),
        rubricsAPI.getRubricByExam(examId),
        examsAPI.exportJSON(examId),
        systemAPI.getHealth(),
        pipelineAPI.getHistory(examId),
      ])
      
      const loadedSubs = subsData.status === 'fulfilled' ? (subsData.value.submissions || []) : []
      setSubmissions(loadedSubs)
      setRubric(rubricData.status === 'fulfilled' ? rubricData.value : null)
      setExamSummary(summaryData.status === 'fulfilled' ? summaryData.value : null)
      
      if (healthData.status === 'fulfilled' && healthData.value.services) {
        setOcrRunning(!!healthData.value.services.ocr)
        setLlmConfigured(!!healthData.value.services.llm)
      }
      
      if (pipelineData.status === 'fulfilled' && pipelineData.value.history) {
        setPipelineTriggered(pipelineData.value.history.length > 0 && pipelineData.value.history.length >= loadedSubs.length)
      } else {
        setPipelineTriggered(false)
      }
    } catch {
      // handled by allSettled
    } finally { setIsLoadingDetails(false) }
  }

  const selectedExam = exams.find(e => e.id === selectedExamId)
  const hasGrades = examSummary && examSummary.total_grades > 0

  const handleExport = async () => {
    if (!selectedExamId) { toast.error('Please select an exam'); return }
    setIsExporting(true)
    try {
      let blob
      if (format === 'csv') {
        const res = await examsAPI.exportCSV(selectedExamId, includeJustification, includePlagiarism)
        blob = new Blob([res], { type: 'text/csv;charset=utf-8;' })
      } else {
        const res = await examsAPI.exportJSON(selectedExamId)
        blob = new Blob([JSON.stringify(res, null, 2)], { type: 'application/json' })
      }
      if (!blob) throw new Error('No data')
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = `grades_${selectedExamId}.${format}`
      document.body.appendChild(a); a.click()
      document.body.removeChild(a); URL.revokeObjectURL(url)
      toast.success(`${format.toUpperCase()} downloaded!`)
    } catch {
      toast.error('Export failed. Make sure the exam has grades.')
    } finally { setIsExporting(false) }
  }

  const formatDate = (iso) => {
    if (!iso) return '—'
    return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  const getStatusBadge = (status) => {
    const s = STATUS_BADGES[status] || STATUS_BADGES.uploaded
    return (
      <span style={{
        padding: '3px 10px', borderRadius: 6, fontSize: 11, fontWeight: 600,
        background: s.bg, border: `1px solid ${s.border}`, color: s.color,
      }}>
        {s.label}
      </span>
    )
  }

  const ToggleSwitch = ({ checked, onChange, label }) => (
    <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, cursor: 'pointer' }}>
      <span style={{ fontSize: 14, color: '#94a3b8' }}>{label}</span>
      <div
        onClick={() => onChange(!checked)}
        style={{
          width: 42, height: 24, borderRadius: 12, position: 'relative',
          background: checked ? 'linear-gradient(135deg,#6366f1,#818cf8)' : 'rgba(255,255,255,0.1)',
          border: `1px solid ${checked ? 'rgba(99,102,241,0.4)' : 'rgba(255,255,255,0.1)'}`,
          transition: 'all 250ms ease', flexShrink: 0, cursor: 'pointer',
          boxShadow: checked ? '0 0 10px rgba(99,102,241,0.3)' : 'none',
        }}
      >
        <div style={{
          position: 'absolute', top: 3,
          left: checked ? 20 : 3,
          width: 16, height: 16, borderRadius: '50%',
          background: '#fff',
          transition: 'left 250ms ease',
          boxShadow: '0 1px 4px rgba(0,0,0,0.3)',
        }} />
      </div>
    </label>
  )

  const StatCard = ({ icon: Icon, color, label, value }) => (
    <div style={{
      padding: '16px 18px', borderRadius: 12,
      background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)',
      display: 'flex', alignItems: 'center', gap: 14,
    }}>
      <div style={{
        width: 40, height: 40, borderRadius: 10,
        background: `${color}15`, border: `1px solid ${color}25`,
        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
      }}>
        <Icon size={20} color={color} />
      </div>
      <div>
        <p style={{ fontSize: 11, color: '#475569', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</p>
        <p style={{ fontSize: 22, fontWeight: 800, color: '#e2e8f0', marginTop: 2 }}>{value}</p>
      </div>
    </div>
  )

  return (
    <Layout>
      <div style={{ animation: 'slideUp 0.4s ease forwards' }}>

        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}>
          <div>
            <h1 style={{ fontSize: 28, fontWeight: 800, color: '#f1f5f9', letterSpacing: '-0.02em' }}>
              Exam Analysis & Export
            </h1>
            <p style={{ color: '#64748b', marginTop: 4, fontSize: 14 }}>
              View submissions, grading status, and download results.
            </p>
          </div>
          {selectedExamId && (
            <button
              onClick={() => loadExamDetails(selectedExamId)}
              className="btn btn-ghost"
              style={{ display: 'flex', alignItems: 'center', gap: 6 }}
            >
              <RefreshCw size={15} /> Refresh
            </button>
          )}
        </div>

        {/* Exam Selector */}
        <div className="glass-card" style={{ padding: 20, marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <Filter size={16} color="#818cf8" />
            <h3 style={{ fontSize: 15, fontWeight: 700, color: '#e2e8f0' }}>Select Exam</h3>
          </div>
          {isLoadingExams ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: '#475569', fontSize: 14 }}>
              <Loader2 size={16} style={{ animation: 'spinSlow 0.8s linear infinite' }} color="#6366f1" />
              Loading exams…
            </div>
          ) : exams.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '24px 0' }}>
              <p style={{ color: '#475569', fontSize: 14 }}>No exams found.</p>
              <button onClick={() => navigate('/upload')} className="btn btn-primary" style={{ marginTop: 12 }}>
                <Upload size={16} /> Create Your First Exam
              </button>
            </div>
          ) : (
            <div style={{ position: 'relative' }}>
              <select
                value={selectedExamId}
                onChange={e => setSelectedExamId(e.target.value)}
                style={{
                  width: '100%', padding: '10px 36px 10px 14px',
                  borderRadius: 10, border: '1px solid rgba(255,255,255,0.1)',
                  background: 'rgba(255,255,255,0.05)', color: '#f1f5f9',
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
                position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none',
              }} />
            </div>
          )}
        </div>

        {/* Loading state */}
        {isLoadingDetails && (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, padding: '48px 0', color: '#64748b' }}>
            <Loader2 size={20} style={{ animation: 'spinSlow 0.8s linear infinite' }} color="#6366f1" />
            <span style={{ fontSize: 14 }}>Loading exam details…</span>
          </div>
        )}

        {/* Main content — only show when we have an exam selected and loaded */}
        {selectedExamId && !isLoadingDetails && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

            {/* Stats Row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
              <StatCard icon={Users} color="#3b82f6" label="Submissions" value={submissions.length} />
              <StatCard icon={BookOpen} color="#8b5cf6" label="Rubric" value={rubric ? `${rubric.max_marks} pts` : 'Not set'} />
              <StatCard icon={BarChart3} color="#10b981" label="Graded" value={examSummary?.total_grades ?? 0} />
              <StatCard icon={Clock} color="#f59e0b" label="Avg Score" value={
                examSummary?.average_marks ? `${Math.round(examSummary.average_marks)}` : '—'
              } />
            </div>

            {/* Submissions List */}
            <div className="glass-card" style={{ overflow: 'hidden' }}>
              <div style={{
                padding: '16px 20px', borderBottom: '1px solid rgba(255,255,255,0.06)',
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              }}>
                <h3 style={{ fontSize: 15, fontWeight: 700, color: '#e2e8f0' }}>
                  Uploaded Submissions <span style={{ color: '#475569', fontWeight: 400 }}>({submissions.length})</span>
                </h3>
                <button
                  onClick={() => navigate(`/upload/${selectedExamId}`)}
                  style={{
                    padding: '5px 12px', borderRadius: 7, fontSize: 12, fontWeight: 600,
                    background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.2)',
                    color: '#93c5fd', cursor: 'pointer', fontFamily: 'Inter, sans-serif',
                    display: 'flex', alignItems: 'center', gap: 5, transition: 'all 150ms ease',
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(59,130,246,0.2)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'rgba(59,130,246,0.1)'}
                >
                  <Upload size={13} /> Add More
                </button>
              </div>

              {submissions.length === 0 ? (
                <div style={{ padding: '40px 20px', textAlign: 'center' }}>
                  <Upload size={36} color="#334155" style={{ marginBottom: 12 }} />
                  <p style={{ fontSize: 14, color: '#475569', marginBottom: 4 }}>No submissions uploaded yet.</p>
                  <p style={{ fontSize: 13, color: '#334155' }}>Upload student PDFs to start grading.</p>
                  <button
                    onClick={() => navigate(`/upload/${selectedExamId}`)}
                    className="btn btn-primary"
                    style={{ marginTop: 16 }}
                  >
                    <Upload size={16} /> Upload PDFs
                  </button>
                </div>
              ) : (
                <div style={{ padding: '12px 20px' }}>
                  {submissions.map((sub, idx) => (
                    <div key={sub.id} style={{
                      display: 'flex', alignItems: 'center', gap: 14,
                      padding: '12px 0',
                      borderBottom: idx < submissions.length - 1 ? '1px solid rgba(255,255,255,0.04)' : 'none',
                    }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: 8,
                        background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.2)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                      }}>
                        <FileText size={16} color="#818cf8" />
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <p style={{ fontSize: 13, fontWeight: 600, color: '#e2e8f0', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {sub.student_name || sub.roll_number || `Submission ${idx + 1}`}
                        </p>
                        <p style={{ fontSize: 11, color: '#475569', marginTop: 2 }}>
                          {formatDate(sub.created_at)}
                        </p>
                      </div>
                      {getStatusBadge(sub.status)}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Grading Status / Pipeline Info */}
            {!hasGrades && submissions.length > 0 && (
              <div style={{
                padding: '20px 24px', borderRadius: 14,
                background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.15)',
                display: 'flex', alignItems: 'flex-start', gap: 16,
              }}>
                <div style={{
                  width: 44, height: 44, borderRadius: 11, flexShrink: 0,
                  background: 'rgba(245,158,11,0.12)', border: '1px solid rgba(245,158,11,0.2)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <AlertCircle size={22} color="#fbbf24" />
                </div>
                <div>
                  <p style={{ fontSize: 15, fontWeight: 700, color: '#fcd34d', marginBottom: 6 }}>
                    AI Grading Not Yet Complete
                  </p>
                  <p style={{ fontSize: 13, color: '#94a3b8', lineHeight: 1.6, marginBottom: 12 }}>
                    Your {submissions.length} submission{submissions.length > 1 ? 's are' : ' is'} uploaded,
                    but the AI grading pipeline hasn't processed them yet. The pipeline requires:
                  </p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {[
                      { done: rubric !== null, text: 'Rubric configured' },
                      { done: ocrRunning, text: 'OCR service running (port 8001)' },
                      { done: llmConfigured, text: 'LLM API key configured (OpenAI / Anthropic / xAI)' },
                      { done: pipelineTriggered, text: 'Pipeline triggered for each submission' },
                    ].map((item, i) => (
                      <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        {item.done
                          ? <CheckCircle2 size={14} color="#10b981" />
                          : <div style={{ width: 14, height: 14, borderRadius: 7, border: '2px solid #475569' }} />
                        }
                        <span style={{ fontSize: 13, color: item.done ? '#6ee7b7' : '#64748b' }}>{item.text}</span>
                      </div>
                    ))}
                  </div>

                  <button
                    onClick={handleTriggerPipeline}
                    disabled={isTriggering || !(ocrRunning && llmConfigured && rubric !== null)}
                    className="btn btn-primary"
                    style={{
                      marginTop: 20,
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 8,
                      opacity: (ocrRunning && llmConfigured && rubric !== null) ? 1 : 0.5,
                      cursor: (ocrRunning && llmConfigured && rubric !== null) ? 'pointer' : 'not-allowed',
                    }}
                  >
                    {isTriggering ? (
                      <Loader2 size={15} style={{ animation: 'spinSlow 0.8s linear infinite' }} />
                    ) : (
                      <Cpu size={15} />
                    )}
                    {isTriggering ? 'Triggering AI Grading...' : 'Trigger AI Grading Now'}
                  </button>
                </div>
              </div>
            )}

            {/* Export Section — only when grades exist */}
            {hasGrades && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 20 }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                  {/* Format */}
                  <div className="glass-card" style={{ padding: 24 }}>
                    <h3 style={{ fontSize: 15, fontWeight: 700, color: '#e2e8f0', marginBottom: 16 }}>Export Format</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                      {[
                        { id: 'csv', label: 'CSV / Excel', icon: FileSpreadsheet, desc: 'Spreadsheet format', color: '#10b981' },
                        { id: 'json', label: 'JSON Data', icon: FileJson, desc: 'Structured data', color: '#f59e0b' },
                      ].map(opt => (
                        <button
                          key={opt.id}
                          onClick={() => setFormat(opt.id)}
                          style={{
                            padding: '16px', borderRadius: 12, cursor: 'pointer',
                            background: format === opt.id ? `${opt.color}12` : 'rgba(255,255,255,0.03)',
                            border: `1px solid ${format === opt.id ? `${opt.color}30` : 'rgba(255,255,255,0.07)'}`,
                            textAlign: 'left', transition: 'all 200ms ease',
                            boxShadow: format === opt.id ? `0 0 16px ${opt.color}18` : 'none',
                          }}
                        >
                          <opt.icon size={22} color={format === opt.id ? opt.color : '#475569'} style={{ marginBottom: 8, display: 'block' }} />
                          <p style={{ fontSize: 14, fontWeight: 700, color: format === opt.id ? opt.color : '#e2e8f0', marginBottom: 2 }}>
                            {opt.label}
                          </p>
                          <p style={{ fontSize: 12, color: '#475569' }}>{opt.desc}</p>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Options */}
                  <div className="glass-card" style={{ padding: 24 }}>
                    <h3 style={{ fontSize: 15, fontWeight: 700, color: '#e2e8f0', marginBottom: 18 }}>Include in Export</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                      <ToggleSwitch checked={includeJustification} onChange={setIncludeJustification} label="AI Grade Justifications" />
                      <div style={{ height: 1, background: 'rgba(255,255,255,0.05)' }} />
                      <ToggleSwitch checked={includePlagiarism} onChange={setIncludePlagiarism} label="Plagiarism Scores" />
                    </div>
                  </div>
                </div>

                {/* Summary + Button */}
                <div style={{ position: 'sticky', top: 24 }}>
                  <div className="glass-card" style={{ padding: 24 }}>
                    <h3 style={{ fontSize: 15, fontWeight: 700, color: '#e2e8f0', marginBottom: 20 }}>Export Summary</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 14, marginBottom: 24 }}>
                      <div>
                        <p style={{ fontSize: 11, color: '#475569', marginBottom: 4, fontWeight: 600, letterSpacing: '0.04em', textTransform: 'uppercase' }}>Exam</p>
                        <p style={{ fontSize: 14, color: '#e2e8f0', fontWeight: 500 }}>{selectedExam?.title || 'None'}</p>
                      </div>
                      <div>
                        <p style={{ fontSize: 11, color: '#475569', marginBottom: 4, fontWeight: 600, letterSpacing: '0.04em', textTransform: 'uppercase' }}>Grades</p>
                        <p style={{ fontSize: 14, color: '#e2e8f0', fontWeight: 500 }}>{examSummary?.total_grades ?? 0} graded</p>
                      </div>
                      <div>
                        <p style={{ fontSize: 11, color: '#475569', marginBottom: 4, fontWeight: 600, letterSpacing: '0.04em', textTransform: 'uppercase' }}>Format</p>
                        <span style={{
                          display: 'inline-flex', padding: '3px 10px', borderRadius: 6,
                          background: format === 'csv' ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)',
                          border: `1px solid ${format === 'csv' ? 'rgba(16,185,129,0.25)' : 'rgba(245,158,11,0.25)'}`,
                          color: format === 'csv' ? '#6ee7b7' : '#fcd34d',
                          fontSize: 13, fontWeight: 700,
                        }}>
                          {format.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={handleExport}
                      disabled={isExporting}
                      className="btn btn-primary btn-full btn-lg"
                    >
                      {isExporting
                        ? <><Loader2 size={17} style={{ animation: 'spinSlow 0.8s linear infinite' }} /> Exporting…</>
                        : <><Download size={17} /> Export Now</>
                      }
                    </button>
                    <p style={{ textAlign: 'center', color: '#334155', fontSize: 12, marginTop: 12 }}>
                      Download starts automatically
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* No grades + no submissions */}
            {!hasGrades && submissions.length === 0 && (
              <div className="glass-card" style={{ padding: '40px 24px', textAlign: 'center' }}>
                <BarChart3 size={40} color="#334155" style={{ marginBottom: 12 }} />
                <h3 style={{ fontSize: 16, fontWeight: 700, color: '#64748b', marginBottom: 6 }}>Nothing to Export Yet</h3>
                <p style={{ fontSize: 13, color: '#475569', marginBottom: 20, maxWidth: 400, margin: '0 auto 20px' }}>
                  Upload student answer sheets first, then the AI grading pipeline will analyze them and produce exportable results.
                </p>
                <button onClick={() => navigate(`/upload/${selectedExamId}`)} className="btn btn-primary">
                  <Upload size={16} /> Upload Student PDFs
                  <ArrowRight size={16} />
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}
