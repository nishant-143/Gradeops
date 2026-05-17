import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Layout from '../components/Layout'
import {
  BookOpen, Plus, Trash2, Save, Loader2, Info, AlertCircle,
} from 'lucide-react'
import { rubricsAPI } from '../api'
import { useToast } from '../hooks'

export default function RubricSetup() {
  const navigate = useNavigate()
  const { examId } = useParams()
  const toast = useToast()

  const [title, setTitle] = useState('')
  const [criteria, setCriteria] = useState([
    { id: 1, name: '', maxMarks: '', description: '' },
  ])
  const [nextId, setNextId] = useState(2)
  const [isSaving, setIsSaving] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [existingRubricId, setExistingRubricId] = useState(null)

  useEffect(() => {
    const fetchExistingRubric = async () => {
      try {
        const data = await rubricsAPI.getRubricByExam(examId)
        if (data && data.criteria && data.criteria.length > 0) {
          setExistingRubricId(data.id)
          setCriteria(data.criteria.map((c, idx) => ({
            id: idx + 1,
            name: c.id,
            maxMarks: c.marks.toString(),
            description: c.description || ''
          })))
          setNextId(data.criteria.length + 1)
        }
      } catch (error) {
        // 404 is expected if no rubric exists yet
        if (error.response?.status !== 404) {
          console.error("Failed to load existing rubric", error)
        }
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchExistingRubric()
  }, [examId])

  const addCriterion = () => {
    setCriteria(prev => [...prev, { id: nextId, name: '', maxMarks: '', description: '' }])
    setNextId(n => n + 1)
  }

  const removeCriterion = (id) => {
    if (criteria.length <= 1) { toast.error('At least one criterion is required'); return }
    setCriteria(prev => prev.filter(c => c.id !== id))
  }

  const updateCriterion = (id, field, value) => {
    setCriteria(prev => prev.map(c => c.id === id ? { ...c, [field]: value } : c))
  }

  const getTotal = () => criteria.reduce((s, c) => s + (parseInt(c.maxMarks) || 0), 0)
  const total = getTotal()

  const saveRubric = async () => {
    if (!title.trim()) { toast.error('Please enter a rubric title'); return }
    if (criteria.some(c => !c.name.trim())) { toast.error('All criteria must have names'); return }
    if (criteria.some(c => !c.maxMarks || parseInt(c.maxMarks) <= 0)) { toast.error('All criteria must have marks > 0'); return }
    if (total === 0) { toast.error('Total marks must be greater than 0'); return }

    setIsSaving(true)
    try {
      const payload = {
        criteria: criteria.map(c => ({
          id: c.name,
          marks: parseInt(c.maxMarks),
          description: c.description,
        })),
        max_marks: total,
      }

      if (existingRubricId) {
        await rubricsAPI.updateRubric(existingRubricId, payload)
        toast.success('Rubric updated successfully!')
      } else {
        await rubricsAPI.createRubric(examId, payload)
        toast.success('Rubric saved! The system will now begin AI grading.')
      }
      setTimeout(() => navigate('/dashboard'), 1200)
    } catch (error) {
      const msg = error.response?.data?.detail ||
        (Array.isArray(error.response?.data)
          ? error.response.data.map(e => e.msg).join(', ')
          : 'Failed to save rubric')
      toast.error(msg)
    } finally { setIsSaving(false) }
  }

  /* marks distribution bar widths */
  const marksBarItems = criteria.map(c => ({
    name: c.name || 'Unnamed',
    marks: parseInt(c.maxMarks) || 0,
  })).filter(c => c.marks > 0)

  const COLORS = ['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899']

  return (
    <Layout>
      <div style={{ maxWidth: 760, margin: '0 auto', animation: 'slideUp 0.4s ease forwards' }}>

        {/* ── Header ── */}
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 28, fontWeight: 800, color: '#f1f5f9', letterSpacing: '-0.02em' }}>
            {existingRubricId ? 'Edit Rubric' : 'Setup Rubric'}
          </h1>
          <p style={{ color: '#64748b', marginTop: 4, fontSize: 14 }}>
            Define grading criteria and point breakdowns. The AI will use this rubric to grade each answer.
          </p>
        </div>

        {/* ── AI Info Banner ── */}
        <div style={{
          padding: '14px 18px',
          borderRadius: 12,
          background: 'rgba(59,130,246,0.07)',
          border: '1px solid rgba(59,130,246,0.18)',
          display: 'flex', alignItems: 'flex-start', gap: 12,
          marginBottom: 24,
        }}>
          <Info size={18} color="#60a5fa" style={{ flexShrink: 0, marginTop: 1 }} />
          <div>
            <p style={{ fontSize: 13, fontWeight: 600, color: '#93c5fd', marginBottom: 3 }}>How AI Uses This Rubric</p>
            <p style={{ fontSize: 13, color: '#64748b', lineHeight: 1.5 }}>
              Each criterion becomes a grading dimension. The LangGraph pipeline evaluates the OCR-extracted answer text against each criterion, assigns marks (0–max), provides a justification, and a confidence score (0–1).
            </p>
          </div>
        </div>

        {/* ── Rubric Builder ── */}
        <div className="glass-card" style={{ overflow: 'hidden', marginBottom: 24 }}>
          {/* Rubric Title */}
          <div style={{ padding: '20px 24px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <label className="label">Rubric Title</label>
            <input
              type="text"
              className="input"
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder="e.g. CS101 Midterm Rubric"
            />
          </div>

          {/* Criteria */}
          <div style={{ padding: '20px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <h3 style={{ fontSize: 15, fontWeight: 700, color: '#e2e8f0' }}>
                Criteria <span style={{ color: '#475569', fontWeight: 400 }}>({criteria.length})</span>
              </h3>
              <div style={{ textAlign: 'right' }}>
                <p style={{ fontSize: 11, color: '#475569', marginBottom: 2 }}>Total Marks</p>
                <p style={{
                  fontSize: 24, fontWeight: 800,
                  background: total > 0 ? 'linear-gradient(135deg,#818cf8,#6366f1)' : 'none',
                  WebkitBackgroundClip: total > 0 ? 'text' : 'unset',
                  WebkitTextFillColor: total > 0 ? 'transparent' : '#475569',
                  backgroundClip: total > 0 ? 'text' : 'unset',
                  color: total > 0 ? 'unset' : '#475569',
                }}>
                  {total}
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {criteria.map((criterion, index) => (
                <div key={criterion.id} style={{
                  padding: '16px 18px',
                  borderRadius: 12,
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid rgba(255,255,255,0.07)',
                  animation: 'slideUp 0.25s ease forwards',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{
                        width: 22, height: 22, borderRadius: 6,
                        background: `${COLORS[index % COLORS.length]}20`,
                        border: `1px solid ${COLORS[index % COLORS.length]}30`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 11, fontWeight: 700, color: COLORS[index % COLORS.length],
                      }}>
                        {index + 1}
                      </div>
                      <p style={{ fontSize: 13, fontWeight: 600, color: '#94a3b8' }}>Criterion {index + 1}</p>
                    </div>
                    <button
                      onClick={() => removeCriterion(criterion.id)}
                      style={{
                        background: 'none', border: 'none', cursor: 'pointer',
                        color: '#475569', padding: 4, display: 'flex',
                        transition: 'color 150ms ease',
                      }}
                      onMouseEnter={e => e.currentTarget.style.color = '#f87171'}
                      onMouseLeave={e => e.currentTarget.style.color = '#475569'}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 120px', gap: 12, marginBottom: 10 }}>
                    <div>
                      <label className="label">Criterion Name</label>
                      <input
                        type="text"
                        className="input"
                        value={criterion.name}
                        onChange={e => updateCriterion(criterion.id, 'name', e.target.value)}
                        placeholder="e.g. Problem Solving Approach"
                      />
                    </div>
                    <div>
                      <label className="label">Max Marks</label>
                      <input
                        type="number"
                        className="input"
                        value={criterion.maxMarks}
                        onChange={e => updateCriterion(criterion.id, 'maxMarks', e.target.value)}
                        placeholder="25"
                        min="1"
                        style={{ textAlign: 'center' }}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="label">Grading Description <span style={{ color: '#334155', fontWeight: 400 }}>(optional – helps AI)</span></label>
                    <textarea
                      className="input textarea"
                      value={criterion.description}
                      onChange={e => updateCriterion(criterion.id, 'description', e.target.value)}
                      placeholder="Describe what constitutes full marks, partial marks, and zero marks for this criterion..."
                      rows={2}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Add criterion */}
            <button
              onClick={addCriterion}
              style={{
                width: '100%', marginTop: 12,
                padding: '12px', borderRadius: 10,
                border: '1px dashed rgba(99,102,241,0.3)',
                background: 'transparent', color: '#818cf8',
                cursor: 'pointer', fontFamily: 'Inter, sans-serif',
                fontSize: 13, fontWeight: 600,
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                transition: 'all 150ms ease',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(99,102,241,0.06)'; e.currentTarget.style.borderColor = 'rgba(99,102,241,0.5)' }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.borderColor = 'rgba(99,102,241,0.3)' }}
            >
              <Plus size={16} />
              Add Criterion
            </button>
          </div>

          {/* Marks Distribution Bar */}
          {total > 0 && marksBarItems.length > 0 && (
            <div style={{ padding: '16px 24px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              <p style={{ fontSize: 12, fontWeight: 600, color: '#475569', marginBottom: 10, letterSpacing: '0.04em', textTransform: 'uppercase' }}>Marks Distribution</p>
              <div style={{ display: 'flex', height: 8, borderRadius: 4, overflow: 'hidden', gap: 2 }}>
                {marksBarItems.map((item, i) => (
                  <div
                    key={item.name}
                    style={{
                      flex: item.marks,
                      background: COLORS[i % COLORS.length],
                      borderRadius: 4,
                      transition: 'flex 0.4s ease',
                    }}
                    title={`${item.name}: ${item.marks} marks`}
                  />
                ))}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 16px', marginTop: 10 }}>
                {marksBarItems.map((item, i) => (
                  <div key={item.name} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <div style={{ width: 8, height: 8, borderRadius: 2, background: COLORS[i % COLORS.length] }} />
                    <span style={{ fontSize: 12, color: '#64748b' }}>{item.name} ({item.marks})</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Summary + Actions */}
          <div style={{
            padding: '16px 24px',
            borderTop: '1px solid rgba(255,255,255,0.06)',
            background: 'rgba(255,255,255,0.02)',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12,
            flexWrap: 'wrap',
          }}>
            <div style={{ display: 'flex', gap: 24 }}>
              <div>
                <p style={{ fontSize: 11, color: '#475569' }}>Criteria</p>
                <p style={{ fontSize: 20, fontWeight: 800, color: '#e2e8f0' }}>{criteria.length}</p>
              </div>
              <div>
                <p style={{ fontSize: 11, color: '#475569' }}>Total Marks</p>
                <p style={{ fontSize: 20, fontWeight: 800, color: '#818cf8' }}>{total}</p>
              </div>
            </div>

            <div style={{ display: 'flex', gap: 10 }}>
              <button
                onClick={() => navigate('/dashboard')}
                className="btn btn-ghost"
              >
                Cancel
              </button>
              <button
                onClick={saveRubric}
                disabled={isSaving || isLoading}
                className="btn btn-primary"
              >
                {isSaving
                  ? <><Loader2 size={16} style={{ animation: 'spinSlow 0.8s linear infinite' }} /> Saving…</>
                  : <><Save size={16} /> {existingRubricId ? 'Update Rubric' : 'Save Rubric'}</>
                }
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
