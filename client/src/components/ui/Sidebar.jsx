import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Upload, Download, ClipboardCheck, LogOut,
  Moon, Sun, GraduationCap, Menu, X, ChevronDown,
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useDarkMode } from '../../hooks/useDarkMode'

const INSTRUCTOR_NAV = [
  { label: 'Dashboard',    icon: LayoutDashboard, path: '/dashboard' },
  { label: 'Upload Exam',  icon: Upload,          path: '/upload'    },
  { label: 'Export Grades',icon: Download,        path: '/export'    },
]
const TA_NAV = [
  { label: 'Review Queue', icon: ClipboardCheck, path: '/review' },
]

export default function Sidebar() {
  const navigate  = useNavigate()
  const location  = useLocation()
  const { user, logout, role } = useAuthStore()
  const { isDark, toggle } = useDarkMode()
  const [menuOpen, setMenuOpen] = useState(false)
  const [userOpen, setUserOpen] = useState(false)

  const handleLogout = () => { logout(); navigate('/login') }
  const navItems = role === 'instructor' ? INSTRUCTOR_NAV : TA_NAV
  const isActive = (path) => location.pathname.startsWith(path)
  const initials  = user?.email?.[0]?.toUpperCase() ?? '?'
  const roleLabel = role === 'instructor' ? 'Instructor' : 'Teaching Assistant'

  return (
    <>
      {/* ── Top Nav Bar ── */}
      <header style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
        height: 54,
        background: 'var(--color-bg-alt)',
        borderBottom: '1px solid var(--color-border)',
        display: 'flex', alignItems: 'center',
        padding: '0 24px',
        gap: 0,
      }}>

        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginRight: 32, flexShrink: 0 }}>
          <div style={{
            width: 28, height: 28, borderRadius: 7,
            background: 'var(--color-primary)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <GraduationCap size={16} color="#fff" />
          </div>
          <span style={{ fontWeight: 700, fontSize: 15, color: 'var(--color-text)', letterSpacing: '-0.01em' }}>
            GradeOps
          </span>
        </div>

        {/* Desktop nav links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
          {navItems.map(item => {
            const active = isActive(item.path)
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 6,
                  padding: '6px 12px', borderRadius: 7, border: 'none',
                  cursor: 'pointer', fontFamily: 'Inter, sans-serif',
                  fontSize: 13, fontWeight: active ? 600 : 400,
                  background: active ? 'var(--color-primary-dim)' : 'transparent',
                  color: active ? 'var(--color-primary-light)' : 'var(--color-text-muted)',
                  transition: 'all 120ms ease',
                  borderBottom: active ? '2px solid var(--color-primary)' : '2px solid transparent',
                  borderRadius: 0,
                  height: 54,
                }}
                onMouseEnter={e => { if (!active) { e.currentTarget.style.color = 'var(--color-text)'; e.currentTarget.style.background = 'var(--color-surface)' }}}
                onMouseLeave={e => { if (!active) { e.currentTarget.style.color = 'var(--color-text-muted)'; e.currentTarget.style.background = 'transparent' }}}
              >
                <item.icon size={15} />
                {item.label}
              </button>
            )
          })}
        </nav>

        {/* Right side */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>

          {/* Theme toggle */}
          <button
            onClick={toggle}
            title="Toggle theme"
            style={{
              width: 32, height: 32, borderRadius: 7, border: '1px solid var(--color-border)',
              background: 'transparent', color: 'var(--color-text-muted)',
              cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
              transition: 'all 120ms ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'var(--color-surface)'; e.currentTarget.style.color = 'var(--color-text)' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--color-text-muted)' }}
          >
            {isDark ? <Sun size={15} /> : <Moon size={15} />}
          </button>

          {/* User dropdown */}
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setUserOpen(v => !v)}
              style={{
                display: 'flex', alignItems: 'center', gap: 7,
                padding: '5px 10px', borderRadius: 7,
                border: '1px solid var(--color-border)',
                background: userOpen ? 'var(--color-surface)' : 'transparent',
                cursor: 'pointer', transition: 'all 120ms ease',
              }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--color-surface)'}
              onMouseLeave={e => { if (!userOpen) e.currentTarget.style.background = 'transparent' }}
            >
              <div style={{
                width: 24, height: 24, borderRadius: '50%',
                background: 'var(--color-primary)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 11, fontWeight: 700, color: '#fff',
              }}>
                {initials}
              </div>
              <span style={{ fontSize: 13, color: 'var(--color-text)', fontFamily: 'Inter, sans-serif', maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {user?.email?.split('@')[0]}
              </span>
              <ChevronDown size={13} color="var(--color-text-faint)" style={{ transform: userOpen ? 'rotate(180deg)' : 'none', transition: 'transform 150ms ease' }} />
            </button>

            {userOpen && (
              <>
                <div style={{ position: 'fixed', inset: 0, zIndex: 49 }} onClick={() => setUserOpen(false)} />
                <div style={{
                  position: 'absolute', top: 'calc(100% + 6px)', right: 0, zIndex: 50,
                  background: 'var(--color-surface)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 10, padding: 6,
                  minWidth: 200,
                  boxShadow: 'var(--shadow-md)',
                  animation: 'slideDown 0.15s ease forwards',
                }}>
                  <div style={{ padding: '8px 10px', marginBottom: 4 }}>
                    <p style={{ fontSize: 13, fontWeight: 500, color: 'var(--color-text)' }}>{user?.email}</p>
                    <p style={{ fontSize: 11, color: 'var(--color-text-faint)', marginTop: 2 }}>{roleLabel}</p>
                  </div>
                  <div style={{ height: 1, background: 'var(--color-border)', margin: '4px 0' }} />
                  <button
                    onClick={handleLogout}
                    style={{
                      width: '100%', display: 'flex', alignItems: 'center', gap: 8,
                      padding: '8px 10px', border: 'none', borderRadius: 7,
                      background: 'transparent', color: 'var(--color-danger)',
                      cursor: 'pointer', fontFamily: 'Inter, sans-serif', fontSize: 13,
                      transition: 'background 120ms ease', textAlign: 'left',
                    }}
                    onMouseEnter={e => e.currentTarget.style.background = 'var(--color-danger-bg)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                  >
                    <LogOut size={14} /> Sign Out
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMenuOpen(v => !v)}
            style={{
              width: 32, height: 32, borderRadius: 7,
              border: '1px solid var(--color-border)',
              background: 'transparent', color: 'var(--color-text-muted)',
              cursor: 'pointer', display: 'none', alignItems: 'center', justifyContent: 'center',
            }}
            className="lg-hidden-flex"
          >
            {menuOpen ? <X size={16} /> : <Menu size={16} />}
          </button>
        </div>
      </header>

      {/* Mobile dropdown nav */}
      {menuOpen && (
        <div style={{
          position: 'fixed', top: 54, left: 0, right: 0, zIndex: 40,
          background: 'var(--color-bg-alt)',
          borderBottom: '1px solid var(--color-border)',
          padding: 12,
        }}>
          {navItems.map(item => (
            <button
              key={item.path}
              onClick={() => { navigate(item.path); setMenuOpen(false) }}
              style={{
                width: '100%', display: 'flex', alignItems: 'center', gap: 9,
                padding: '10px 14px', borderRadius: 8, border: 'none',
                cursor: 'pointer', fontFamily: 'Inter, sans-serif', fontSize: 14,
                background: isActive(item.path) ? 'var(--color-primary-dim)' : 'transparent',
                color: isActive(item.path) ? 'var(--color-primary-light)' : 'var(--color-text-muted)',
                marginBottom: 4, textAlign: 'left',
              }}
            >
              <item.icon size={16} /> {item.label}
            </button>
          ))}
        </div>
      )}

      {/* Spacer so content doesn't hide under fixed navbar */}
      <div style={{ height: 54, flexShrink: 0, width: '100%' }} />
    </>
  )
}
