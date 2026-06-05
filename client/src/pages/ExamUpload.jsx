import React, { useState, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Layout from '../components/Layout'
import {
  Upload, FileText, Plus, Trash2, ArrowRight, CheckCircle2,
  BookOpen, Cpu, ClipboardCheck, Download, Loader2, FilePlus, X,
} from 'lucide-react'
import { submissionsAPI, examsAPI } from '../api'
import { useToast } from '../hooks'

const STEPS = [
  { num: 1, label: 'Create Exam',  sub: 'Title & metadata'   },
  { num: 2, label: 'Upload PDFs',  sub: 'Student submissions' },
  { num: 3, label: 'Setup Rubric', sub: 'Grading criteria'   },
]

const NEXT_STEPS = [
  { icon: Cpu,            color: '#3b82f6', label: 'OCR & Splitting',  desc: 'System splits PDFs into pages and crops answer regions' },
  { icon: Cpu,            color: '#8b5cf6', label: 'AI Grading',       desc: 'Qwen-VL OCR extracts text, LangGraph pipeline grades each answer' },
  { icon: ClipboardCheck, color: '#f59e0b', label: 'TA Review',        desc: 'TAs review AI grades, approve or override with justification' },
  { icon: Download,       color: '#10b981', label: 'Export',           desc: 'You export final grades as CSV or PDF' },
]

export default function ExamUpload() {
  const navigate = useNavigate()
  const { examId } = useParams()
  const toast = useToast()
  const fileInputRef = useRef(null)

  const [examTitle, setExamTitle] = useState('')
  const [examDescription, setExamDescription] = useState('')
  const [files, setFiles] = useState([])
  const [uploadProgress, setUploadProgress] = useState({})
  const [uploadingFileIndex, setUploadingFileIndex] = useState(null)
  const [isCreatingExam, setIsCreatingExam] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [newExamId, setNewExamId] = useState(examId || null)
  const [step, setStep] = useState(examId ? 2 : 1)

  /* ── File handling ── */
  const addFiles = (newFiles) => {
    const pdfs = newFiles.filter(f => f.type === 'application/pdf')
    if (pdfs.length !== newFiles.length) toast.error('Only PDF files are supported')
    if (pdfs.length > 0) setFiles(prev => [...prev, ...pdfs])
  }

  const handleDrop = (e) => {
    e.preventDefault(); setIsDragging(false)
    addFiles(Array.from(e.dataTransfer.files))
  }

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
    setUploadProgress(prev => { const n = { ...prev }; delete n[index]; return n })
  }

  /* ── API calls ── */
  const createExam = async () => {
    if (!examTitle.trim()) { toast.error('Please enter an exam title'); return }
    setIsCreatingExam(true)
    try {
      const response = await examsAPI.createExam(examTitle, examDescription)
      setNewExamId(response.id)
      toast.success('Exam created! Now upload student PDFs.')
      setStep(2)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create exam')
    } finally { setIsCreatingExam(false) }
  }

  const uploadFiles = async () => {
    if (files.length === 0) { toast.error('Please select at least one PDF'); return }
    let successCount = 0
    for (let i = 0; i < files.length; i++) {
      setUploadingFileIndex(i)
      try {
        await submissionsAPI.uploadSubmission(newExamId, files[i])
        setUploadProgress(prev => ({ ...prev, [i]: 'done' }))
        successCount++
      } catch (err) {
        const detail = err.response?.data?.detail || `Failed to upload ${files[i].name}`
        toast.error(detail)
        setUploadProgress(prev => ({ ...prev, [i]: 'error' }))
      }
    }
    setUploadingFileIndex(null)
    if (successCount > 0) {
      toast.success(`${successCount} file${successCount > 1 ? 's' : ''} uploaded successfully!`)
      setStep(3)
    } else {
      toast.error('All uploads failed. Check the backend server logs.')
    }
  }

  const formatSize = (bytes) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`
  }

  return (
    <Layout>
      <div style={{ maxWidth: 760, margin: '0 auto', animation: 'slideUp 0.4s ease forwards' }}>

        {/* ── Header ── */}
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 28, fontWeight: 800, color: '#f1f5f9', letterSpacing: '-0.02em' }}>
            {examId ? 'Upload Student PDFs' : 'Upload Exam'}
          </h1>
          <p style={{ color: '#64748b', marginTop: 4, fontSize: 14 }}>
            {examId 
              ? 'Upload student PDF submissions for this exam.' 
              : 'Create an exam, upload student PDFs, then set up the grading rubric.'}
          </p>
        </div>

        {/* ── Step Indicator ── */}
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 32 }}>
          {STEPS.map((s, idx) => (
            <React.Fragment key={s.num}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{
                  width: 36, height: 36, borderRadius: '50%',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontWeight: 700, fontSize: 14,
                  background: step > s.num
                    ? 'rgba(16,185,129,0.2)'
                    : step === s.num
                    ? 'linear-gradient(135deg,#6366f1,#818cf8)'
                    : 'rgba(255,255,255,0.06)',
                  color: step > s.num ? '#6ee7b7' : step === s.num ? '#fff' : '#475569',
                  border: step === s.num ? 'none' : `1px solid ${step > s.num ? 'rgba(16,185,129,0.3)' : 'rgba(255,255,255,0.08)'}`,
                  boxShadow: step === s.num ? '0 4px 14px rgba(99,102,241,0.4)' : 'none',
                  flexShrink: 0,
                }}>
                  {step > s.num ? <CheckCircle2 size={18} /> : s.num}
                </div>
                <div>
                  <p style={{ fontSize: 13, fontWeight: step >= s.num ? 600 : 400, color: step >= s.num ? '#e2e8f0' : '#475569' }}>
                    {s.label}
                  </p>
                  <p style={{ fontSize: 11, color: '#334155' }}>{s.sub}</p>
                </div>
              </div>

              {idx < STEPS.length - 1 && (
                <div style={{
                  flex: 1, height: 2, margin: '0 12px', marginBottom: 16,
                  background: step > s.num
                    ? 'linear-gradient(90deg,rgba(16,185,129,0.4),rgba(16,185,129,0.2))'
                    : 'rgba(255,255,255,0.06)',
                  borderRadius: 2,
                  transition: 'all 0.5s ease',
                }} />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* ── STEP 1: Create Exam ── */}
        {step === 1 && (
          <div className="glass-card" style={{ padding: 32, animation: 'slideUp 0.3s ease forwards' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 28 }}>
              <div style={{
                width: 40, height: 40, borderRadius: 10,
                background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.25)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <FilePlus size={20} color="#818cf8" />
              </div>
              <div>
                <h2 style={{ fontSize: 18, fontWeight: 700, color: '#f1f5f9' }}>Create Exam</h2>
                <p style={{ fontSize: 13, color: '#64748b' }}>Give your exam a name and optional description</p>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
              <div>
                <label className="label">Exam Title *</label>
                <input
                  type="text"
                  className="input"
                  value={examTitle}
                  onChange={e => setExamTitle(e.target.value)}
                  placeholder="e.g. CS101 Midterm Examination"
                  onKeyDown={e => e.key === 'Enter' && createExam()}
                />
              </div>

              <div>
                <label className="label">Description <span style={{ color: '#334155', fontWeight: 400 }}>(optional)</span></label>
                <textarea
                  className="input textarea"
                  value={examDescription}
                  onChange={e => setExamDescription(e.target.value)}
                  placeholder="Add any notes about this exam..."
                  rows={3}
                />
              </div>

              <button
                onClick={createExam}
                disabled={isCreatingExam}
                className="btn btn-primary btn-full btn-lg"
                style={{ marginTop: 4 }}
              >
                {isCreatingExam
                  ? <><Loader2 size={18} style={{ animation: 'spinSlow 0.8s linear infinite' }} /> Creating…</>
                  : <><Plus size={18} /> Create Exam</>
                }
              </button>
            </div>
          </div>
        )}

        {/* ── STEP 2: Upload PDFs ── */}
        {step === 2 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20, animation: 'slideLeft 0.3s ease forwards' }}>
            {/* Drag-and-drop zone */}
            <div
              onDragOver={e => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              style={{
                padding: '48px 32px',
                borderRadius: 16,
                border: `2px dashed ${isDragging ? '#6366f1' : 'rgba(255,255,255,0.1)'}`,
                background: isDragging ? 'rgba(99,102,241,0.06)' : 'rgba(255,255,255,0.02)',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 200ms ease',
                boxShadow: isDragging ? '0 0 0 4px rgba(99,102,241,0.15)' : 'none',
              }}
            >
              <div style={{
                width: 64, height: 64, borderRadius: 16,
                background: isDragging ? 'rgba(99,102,241,0.2)' : 'rgba(255,255,255,0.05)',
                border: `1px solid ${isDragging ? 'rgba(99,102,241,0.4)' : 'rgba(255,255,255,0.08)'}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 16px',
                transition: 'all 200ms ease',
              }}>
                <Upload size={28} color={isDragging ? '#818cf8' : '#475569'} />
              </div>
              <h3 style={{ fontSize: 18, fontWeight: 700, color: isDragging ? '#a5b4fc' : '#e2e8f0', marginBottom: 8 }}>
                {isDragging ? 'Drop files here!' : 'Drag & Drop PDF Files'}
              </h3>
              <p style={{ color: '#475569', fontSize: 14, marginBottom: 16 }}>
                or click to browse your computer
              </p>
              <span style={{
                display: 'inline-block', padding: '6px 16px', borderRadius: 8,
                background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.25)',
                color: '#818cf8', fontSize: 12, fontWeight: 600,
              }}>
                PDF only · Max 50 MB per file
              </span>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf"
                onChange={e => addFiles(Array.from(e.target.files))}
                style={{ display: 'none' }}
              />
            </div>

            {/* File list */}
            {files.length > 0 && (
              <div className="glass-card" style={{ padding: 20 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                  <h3 style={{ fontSize: 15, fontWeight: 700, color: '#e2e8f0' }}>
                    Selected Files <span style={{ color: '#64748b', fontWeight: 400 }}>({files.length})</span>
                  </h3>
                  {uploadingFileIndex === null && (
                    <button
                      onClick={() => setFiles([])}
                      style={{ background: 'none', border: 'none', color: '#475569', cursor: 'pointer', display: 'flex', gap: 4, alignItems: 'center', fontSize: 12, fontFamily: 'Inter, sans-serif' }}
                    >
                      <X size={14} /> Clear all
                    </button>
                  )}
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {files.map((file, i) => {
                    const prog = uploadProgress[i]
                    return (
                      <div key={i} style={{
                        display: 'flex', alignItems: 'center', gap: 12,
                        padding: '12px 14px', borderRadius: 10,
                        background: prog === 'done' ? 'rgba(16,185,129,0.06)' : prog === 'error' ? 'rgba(239,68,68,0.06)' : 'rgba(255,255,255,0.03)',
                        border: `1px solid ${prog === 'done' ? 'rgba(16,185,129,0.15)' : prog === 'error' ? 'rgba(239,68,68,0.15)' : 'rgba(255,255,255,0.06)'}`,
                      }}>
                        <FileText size={18} color={prog === 'error' ? '#f87171' : '#818cf8'} style={{ flexShrink: 0 }} />
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <p style={{ fontSize: 13, fontWeight: 500, color: '#e2e8f0', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {file.name}
                          </p>
                          <p style={{ fontSize: 11, color: '#475569', marginTop: 2 }}>{formatSize(file.size)}</p>
                        </div>
                        <div style={{ flexShrink: 0 }}>
                          {prog === 'done' && <CheckCircle2 size={18} color="#10b981" />}
                          {prog === 'error' && <span style={{ fontSize: 12, color: '#f87171', fontWeight: 600 }}>Error</span>}
                          {uploadingFileIndex === i && <Loader2 size={18} color="#818cf8" style={{ animation: 'spinSlow 0.8s linear infinite' }} />}
                          {prog === undefined && uploadingFileIndex !== i && (
                            <button onClick={() => removeFile(i)} style={{ background: 'none', border: 'none', color: '#475569', cursor: 'pointer', padding: 4, display: 'flex' }}>
                              <Trash2 size={16} />
                            </button>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>

                {uploadingFileIndex === null && (
                  <button
                    onClick={uploadFiles}
                    className="btn btn-primary btn-full"
                    style={{ marginTop: 16 }}
                  >
                    <Upload size={16} />
                    Upload {files.length} File{files.length > 1 ? 's' : ''}
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {/* ── STEP 3: What Happens Next ── */}
        {step === 3 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20, animation: 'slideLeft 0.3s ease forwards' }}>
            {/* Success banner */}
            <div style={{
              padding: '24px 28px',
              borderRadius: 16,
              background: 'rgba(16,185,129,0.08)',
              border: '1px solid rgba(16,185,129,0.2)',
              display: 'flex', alignItems: 'center', gap: 16,
            }}>
              <div style={{
                width: 52, height: 52, borderRadius: '50%',
                background: 'rgba(16,185,129,0.15)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
              }}>
                <CheckCircle2 size={28} color="#10b981" />
              </div>
              <div>
                <h2 style={{ fontSize: 18, fontWeight: 700, color: '#6ee7b7' }}>Files Uploaded Successfully!</h2>
                <p style={{ fontSize: 14, color: '#64748b', marginTop: 3 }}>
                  {files.length} PDF file{files.length > 1 ? 's' : ''} are ready for processing.
                </p>
              </div>
            </div>

            {/* Backend pipeline explainer */}
            <div className="glass-card" style={{ padding: 24 }}>
              <p style={{ fontSize: 12, fontWeight: 700, color: '#475569', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 20 }}>
                What happens next (automatic)
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {NEXT_STEPS.map((ns, i) => (
                  <div key={ns.label} style={{
                    display: 'flex', alignItems: 'flex-start', gap: 14,
                    padding: '14px 16px', borderRadius: 10,
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(255,255,255,0.06)',
                    animation: `slideUp 0.3s ease ${i * 0.08}s forwards`, opacity: 0,
                  }}>
                    <div style={{
                      width: 36, height: 36, borderRadius: 9, flexShrink: 0,
                      background: `${ns.color}15`, border: `1px solid ${ns.color}25`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <ns.icon size={18} color={ns.color} />
                    </div>
                    <div>
                      <p style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0' }}>{ns.label}</p>
                      <p style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>{ns.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* CTA */}
            {examId ? (
              <button
                onClick={() => navigate(`/export/${newExamId}`)}
                className="btn btn-primary btn-full btn-lg"
              >
                Go to Export / Analysis
                <ArrowRight size={18} />
              </button>
            ) : (
              <button
                onClick={() => navigate(`/rubric/${newExamId}`)}
                className="btn btn-primary btn-full btn-lg"
              >
                Setup Grading Rubric
                <ArrowRight size={18} />
              </button>
            )}

            <button
              onClick={() => navigate('/dashboard')}
              className="btn btn-ghost btn-full"
            >
              Go to Dashboard
            </button>
          </div>
        )}
      </div>
    </Layout>
  )
}
