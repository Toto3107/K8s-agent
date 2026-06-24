'use client'

interface Step {
  label: string
  status: 'pending' | 'running' | 'done' | 'error'
}

interface InvestigationPanelProps {
  steps: Step[]
  isRunning: boolean
}

const STATUS_ICONS = {
  pending: <span className="text-terminal-muted">○</span>,
  running: <span className="text-terminal-accent animate-pulse">◉</span>,
  done: <span className="text-terminal-green">✓</span>,
  error: <span className="text-terminal-red">✗</span>,
}

export function InvestigationPanel({ steps, isRunning }: InvestigationPanelProps) {
  return (
    <div className="p-5 rounded-lg border border-terminal-border bg-terminal-card animate-fade-in">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-terminal-dim text-xs font-mono uppercase tracking-widest">
          Investigation Progress
        </span>
        {isRunning && (
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-terminal-accent animate-pulse" />
            <span className="text-terminal-accent text-xs font-mono">Running</span>
          </span>
        )}
      </div>

      <div className="space-y-2">
        {steps.map((step, i) => (
          <div
            key={i}
            className={`
              flex items-center gap-3 p-2 rounded
              ${step.status === 'running' ? 'bg-terminal-accent/5' : ''}
              ${step.status === 'done' ? 'opacity-80' : ''}
              ${step.status === 'pending' ? 'opacity-40' : ''}
            `}
          >
            <span className="w-4 text-center font-mono">
              {STATUS_ICONS[step.status]}
            </span>
            <span className={`
              font-mono text-sm
              ${step.status === 'done' ? 'text-terminal-text' : ''}
              ${step.status === 'running' ? 'text-terminal-accent' : ''}
              ${step.status === 'pending' ? 'text-terminal-dim' : ''}
              ${step.status === 'error' ? 'text-terminal-red' : ''}
            `}>
              {step.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
