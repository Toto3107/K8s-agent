'use client'

import { useState, useEffect } from 'react'

export function Header() {
  const [time, setTime] = useState<string | null>(null)

  useEffect(() => {
    // Only run on client — avoids server/client mismatch
    setTime(new Date().toLocaleTimeString())
    const interval = setInterval(() => {
      setTime(new Date().toLocaleTimeString())
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="border-b border-terminal-border pb-6">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-3 h-3 rounded-full bg-terminal-accent glow-accent" />
            <span className="text-terminal-accent font-mono text-xs tracking-widest uppercase">
              AI Kubernetes Agent
            </span>
          </div>
          <h1 className="text-3xl font-bold text-terminal-text">
            Cluster Troubleshooter
          </h1>
          <p className="text-terminal-dim mt-1 text-sm">
            AI-powered Kubernetes root cause analysis — behaves like a Senior SRE
          </p>
        </div>

        <div className="text-right hidden sm:block">
          <div className="flex items-center gap-2 justify-end mb-1">
            <span className="status-dot healthy" />
            <span className="text-terminal-dim text-xs font-mono">API Online</span>
          </div>
          <div className="text-terminal-dim text-xs font-mono">
            {time ?? '—'}
          </div>
        </div>
      </div>
    </div>
  )
}
