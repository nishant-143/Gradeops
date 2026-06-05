import React from 'react'
import Sidebar from './ui/Sidebar'

export default function Layout({ children, className = '' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: 'var(--color-bg)' }}>
      <Sidebar />
      <main style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden' }} className={className}>
        <div style={{ padding: '28px 32px', maxWidth: '1280px', margin: '0 auto' }}>
          {children}
        </div>
      </main>
    </div>
  )
}
