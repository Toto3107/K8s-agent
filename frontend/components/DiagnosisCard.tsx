'use client'

interface Diagnosis {
  root_cause: string
  explanation: string
  fix: string
  kubectl_commands: string[]
  prevention: string
  confidence: number
  severity: string
  affected_resources: string[]
}

const SEVERITY_COLORS = {
  critical: 'text-terminal-red border-terminal-red/40 bg-terminal-red/5',
  high: 'text-terminal-yellow border-terminal-yellow/40 bg-terminal-yellow/5',
  medium: 'text-terminal-accent border-terminal-accent/40 bg-terminal-accent/5',
  low: 'text-terminal-green border-terminal-green/40 bg-terminal-green/5',
  unknown: 'text-terminal-dim border-terminal-border bg-terminal-card',
}

function ConfidenceBar({ value }: { value: number }) {
  const color = value >= 80 ? '#00ff88' : value >= 60 ? '#ffd60a' : '#ff4d6d'
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-1.5 bg-terminal-border rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${value}%`, backgroundColor: color }}
        />
      </div>
      <span className="font-mono text-sm font-semibold" style={{ color }}>
        {value}%
      </span>
    </div>
  )
}

export function DiagnosisCard({ diagnosis }: { diagnosis: Diagnosis }) {
  const severityClass = SEVERITY_COLORS[diagnosis.severity as keyof typeof SEVERITY_COLORS] || SEVERITY_COLORS.unknown

  return (
    <div className="rounded-lg border border-terminal-border bg-terminal-card overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-terminal-border flex items-center justify-between">
        <span className="text-terminal-dim text-xs font-mono uppercase tracking-widest">
          AI Diagnosis
        </span>
        <span className={`text-xs font-mono px-2 py-0.5 rounded border ${severityClass}`}>
          {diagnosis.severity?.toUpperCase() || 'UNKNOWN'}
        </span>
      </div>

      <div className="p-5 space-y-5">
        {/* Root Cause */}
        <div>
          <label className="text-terminal-dim text-xs font-mono uppercase tracking-widest block mb-1.5">
            Root Cause
          </label>
          <p className="text-terminal-text font-semibold">{diagnosis.root_cause}</p>
        </div>

        {/* Explanation */}
        <div>
          <label className="text-terminal-dim text-xs font-mono uppercase tracking-widest block mb-1.5">
            Explanation
          </label>
          <p className="text-terminal-dim text-sm leading-relaxed">{diagnosis.explanation}</p>
        </div>

        {/* Fix */}
        <div>
          <label className="text-terminal-dim text-xs font-mono uppercase tracking-widest block mb-1.5">
            Suggested Fix
          </label>
          <div className="p-3 bg-terminal-bg rounded border border-terminal-border">
            <p className="text-terminal-text text-sm whitespace-pre-wrap">{diagnosis.fix}</p>
          </div>
        </div>

        {/* kubectl Commands */}
        {diagnosis.kubectl_commands?.length > 0 && (
          <div>
            <label className="text-terminal-dim text-xs font-mono uppercase tracking-widest block mb-1.5">
              kubectl Commands
            </label>
            <div className="space-y-1.5">
              {diagnosis.kubectl_commands.map((cmd, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 p-2 bg-terminal-bg rounded border border-terminal-border/50 group cursor-pointer"
                  onClick={() => navigator.clipboard?.writeText(cmd)}
                  title="Click to copy"
                >
                  <span className="text-terminal-accent font-mono text-xs">$</span>
                  <code className="text-terminal-green font-mono text-xs flex-1">{cmd}</code>
                  <span className="text-terminal-dim text-xs opacity-0 group-hover:opacity-100 transition-opacity">copy</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Affected Resources */}
        {diagnosis.affected_resources?.length > 0 && (
          <div>
            <label className="text-terminal-dim text-xs font-mono uppercase tracking-widest block mb-1.5">
              Affected Resources
            </label>
            <div className="flex flex-wrap gap-1.5">
              {diagnosis.affected_resources.map((r, i) => (
                <span key={i} className="text-xs font-mono px-2 py-0.5 bg-terminal-bg border border-terminal-border rounded text-terminal-purple">
                  {r}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Confidence */}
        <div>
          <label className="text-terminal-dim text-xs font-mono uppercase tracking-widest block mb-1.5">
            Confidence
          </label>
          <ConfidenceBar value={diagnosis.confidence || 0} />
        </div>

        {/* Prevention */}
        {diagnosis.prevention && (
          <div className="pt-3 border-t border-terminal-border">
            <label className="text-terminal-dim text-xs font-mono uppercase tracking-widest block mb-1.5">
              Prevention
            </label>
            <p className="text-terminal-dim text-xs leading-relaxed">{diagnosis.prevention}</p>
          </div>
        )}
      </div>
    </div>
  )
}
