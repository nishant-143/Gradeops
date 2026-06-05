import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, Lock, Eye, EyeOff, GraduationCap, Loader2, CheckCircle } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { authAPI } from '../api'
import { useToast } from '../hooks'

const FEATURES = [
  'AI-powered OCR extracts handwritten answers',
  'LangGraph pipeline grades with rubric precision',
  'TA review queue for approval or override',
  'One-click CSV / PDF grade export',
]

const inputBase = {
  width: '100%',
  padding: '10px 12px 10px 38px',
  fontSize: 14,
  fontFamily: 'Inter, sans-serif',
  background: '#0d1117',
  border: '1px solid #263044',
  borderRadius: 8,
  color: '#e2e8f0',
  outline: 'none',
  transition: 'border-color 120ms ease',
}

function Field({ icon: Icon, type, value, onChange, placeholder, disabled, right }) {
  return (
    <div style={{ position: 'relative' }}>
      <Icon size={15} style={{ position: 'absolute', left: 11, top: '50%', transform: 'translateY(-50%)', color: '#3d4f66', pointerEvents: 'none' }} />
      <input
        type={type} value={value} onChange={onChange}
        placeholder={placeholder} disabled={disabled} style={inputBase}
        onFocus={e => { e.target.style.borderColor = '#14b8a6'; e.target.style.boxShadow = '0 0 0 3px rgba(20,184,166,0.14)' }}
        onBlur={e => { e.target.style.borderColor = '#263044'; e.target.style.boxShadow = 'none' }}
      />
      {right && <div style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)' }}>{right}</div>}
    </div>
  )
}

export default function Login() {
  const navigate = useNavigate()
  const { setUser, setLoading } = useAuthStore()
  const toast = useToast()

  const [email, setEmail]           = useState('')
  const [password, setPassword]     = useState('')
  const [showPwd, setShowPwd]       = useState(false)
  const [isLoading, setIsLoading]   = useState(false)
  const [tab, setTab]               = useState('login')
  const [role, setRole]             = useState('instructor')

  const handleLogin = async (e) => {
    e.preventDefault()
    if (!email || !password) { toast.error('Email and password are required'); return }
    setIsLoading(true); setLoading(true)
    try {
      const { access_token, user } = await authAPI.login(email, password)
      setUser(user, access_token)
      toast.success(`Welcome back, ${user.email}!`)
      setTimeout(() => navigate(user.role === 'instructor' ? '/dashboard' : '/review'), 500)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally { setIsLoading(false); setLoading(false) }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    if (!email || !password) { toast.error('Email and password are required'); return }
    if (password.length < 6) { toast.error('Password must be at least 6 characters'); return }
    setIsLoading(true); setLoading(true)
    try {
      const { access_token, user } = await authAPI.register(email, password, role)
      setUser(user, access_token)
      toast.success('Account created! Welcome to GradeOps.')
      setTimeout(() => navigate(role === 'instructor' ? '/dashboard' : '/review'), 500)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally { setIsLoading(false); setLoading(false) }
  }

  const eyeBtn = (
    <button type="button" onClick={() => setShowPwd(v => !v)}
      style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#3d4f66', display: 'flex', padding: 0 }}>
      {showPwd ? <EyeOff size={14} /> : <Eye size={14} />}
    </button>
  )

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: '#0d1117' }}>

      {/* ── Left panel ── */}
      <div style={{
        display: 'none',  /* hidden on mobile — shown via media query workaround below */
        flex: '0 0 460px',
        background: 'linear-gradient(160deg, #0f2027 0%, #0d1a26 50%, #0a1a18 100%)',
        borderRight: '1px solid #1a2a38',
        padding: '56px 48px',
        flexDirection: 'column',
        justifyContent: 'space-between',
        position: 'relative',
        overflow: 'hidden',
      }} className="login-left-panel">

        {/* Teal glow blob */}
        <div style={{
          position: 'absolute', bottom: -80, left: -80, width: 340, height: 340,
          borderRadius: '50%', background: 'radial-gradient(circle, rgba(20,184,166,0.12) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div>
          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 56 }}>
            <div style={{ width: 38, height: 38, borderRadius: 10, background: '#14b8a6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <GraduationCap size={22} color="#fff" />
            </div>
            <span style={{ fontWeight: 700, fontSize: 20, color: '#e2e8f0', letterSpacing: '-0.02em' }}>GradeOps</span>
          </div>

          {/* Headline */}
          <h2 style={{ fontSize: 30, fontWeight: 700, color: '#e2e8f0', lineHeight: 1.25, letterSpacing: '-0.02em', marginBottom: 14 }}>
            Grade smarter,<br />not harder.
          </h2>
          <p style={{ fontSize: 14, color: '#7a8ba0', lineHeight: 1.7, marginBottom: 40 }}>
            AI-assisted exam grading that cuts marking time while keeping human judgement at the center.
          </p>

          {/* Features */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {FEATURES.map(f => (
              <div key={f} style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                <CheckCircle size={16} color="#14b8a6" style={{ marginTop: 2, flexShrink: 0 }} />
                <span style={{ fontSize: 13, color: '#94a3b8', lineHeight: 1.5 }}>{f}</span>
              </div>
            ))}
          </div>
        </div>

        <p style={{ fontSize: 12, color: '#3d4f66' }}>© 2025 GradeOps · Academic Integrity First</p>
      </div>

      {/* ── Right panel (form) ── */}
      <div style={{
        flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: '40px 24px',
      }}>
        <div style={{ width: '100%', maxWidth: 380, animation: 'slideUp 0.25s ease forwards' }}>

          {/* Mobile-only brand */}
          <div style={{ textAlign: 'center', marginBottom: 28 }} className="login-mobile-brand">
            <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 42, height: 42, borderRadius: 11, background: '#14b8a6', marginBottom: 10 }}>
              <GraduationCap size={22} color="#fff" />
            </div>
            <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e2e8f0' }}>GradeOps</h1>
          </div>

          <h3 style={{ fontSize: 20, fontWeight: 600, color: '#e2e8f0', marginBottom: 4 }}>
            {tab === 'login' ? 'Sign in to your account' : 'Create a new account'}
          </h3>
          <p style={{ fontSize: 13, color: '#7a8ba0', marginBottom: 28 }}>
            {tab === 'login' ? "Don't have an account? " : 'Already have an account? '}
            <button onClick={() => setTab(tab === 'login' ? 'register' : 'login')}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#14b8a6', fontSize: 13, fontFamily: 'Inter, sans-serif', fontWeight: 500, padding: 0 }}>
              {tab === 'login' ? 'Sign up' : 'Sign in'}
            </button>
          </p>

          {/* Form */}
          <form onSubmit={tab === 'login' ? handleLogin : handleRegister}
            style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#7a8ba0', marginBottom: 5, letterSpacing: '0.05em', textTransform: 'uppercase' }}>Email</label>
              <Field icon={Mail} type="email" value={email} onChange={e => setEmail(e.target.value)}
                placeholder="you@university.edu" disabled={isLoading} />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#7a8ba0', marginBottom: 5, letterSpacing: '0.05em', textTransform: 'uppercase' }}>Password</label>
              <Field icon={Lock} type={showPwd ? 'text' : 'password'} value={password}
                onChange={e => setPassword(e.target.value)} placeholder="••••••••"
                disabled={isLoading} right={eyeBtn} />
            </div>

            {tab === 'register' && (
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#7a8ba0', marginBottom: 5, letterSpacing: '0.05em', textTransform: 'uppercase' }}>Role</label>
                <select value={role} onChange={e => setRole(e.target.value)} disabled={isLoading}
                  style={{ ...inputBase, paddingLeft: 12, cursor: 'pointer', appearance: 'none' }}>
                  <option value="instructor" style={{ background: '#0d1117' }}>Instructor</option>
                  <option value="ta" style={{ background: '#0d1117' }}>Teaching Assistant</option>
                </select>
              </div>
            )}

            <button type="submit" disabled={isLoading}
              style={{
                width: '100%', padding: '11px', borderRadius: 8, border: 'none',
                background: '#14b8a6', color: '#fff',
                fontSize: 14, fontWeight: 600, fontFamily: 'Inter, sans-serif',
                cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                transition: 'background 120ms ease', marginTop: 4,
                opacity: isLoading ? 0.7 : 1,
              }}
              onMouseEnter={e => { if (!isLoading) e.currentTarget.style.background = '#0d9488' }}
              onMouseLeave={e => e.currentTarget.style.background = '#14b8a6'}
            >
              {isLoading && <Loader2 size={16} style={{ animation: 'spinSlow 1s linear infinite' }} />}
              {isLoading ? (tab === 'login' ? 'Signing in…' : 'Creating account…') : (tab === 'login' ? 'Sign In' : 'Create Account')}
            </button>
          </form>

          <p style={{ textAlign: 'center', color: '#3d4f66', fontSize: 11, marginTop: 24 }}>
            Secure · AI-Powered · Academic Integrity
          </p>
        </div>
      </div>

      {/* Style to show left panel on wider screens */}
      <style>{`
        @media (min-width: 768px) {
          .login-left-panel { display: flex !important; }
          .login-mobile-brand { display: none !important; }
        }
      `}</style>
    </div>
  )
}
