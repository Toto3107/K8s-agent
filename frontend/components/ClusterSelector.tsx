'use client'

interface Cluster {
  name: string
  is_current: boolean
  raw?: string
}

interface ClusterSelectorProps {
  clusters: Cluster[]
  isLoading: boolean
  selected: string | null
  onSelect: (name: string | null) => void
}

export function ClusterSelector({ clusters, isLoading, selected, onSelect }: ClusterSelectorProps) {
  if (isLoading) {
    return (
      <div className="p-4 rounded-lg border border-terminal-border bg-terminal-card">
        <p className="text-terminal-dim text-sm font-mono animate-pulse">Loading clusters from kubeconfig...</p>
      </div>
    )
  }

  if (clusters.length === 0) {
    return (
      <div className="p-4 rounded-lg border border-terminal-yellow/30 bg-terminal-yellow/5">
        <p className="text-terminal-yellow text-sm font-mono">
          ⚠ No clusters found in kubeconfig. Make sure kubectl is configured.
        </p>
        <p className="text-terminal-dim text-xs font-mono mt-1">
          Run: <span className="text-terminal-accent">kubectl config get-contexts</span>
        </p>
      </div>
    )
  }

  return (
    <div>
      <p className="text-terminal-dim text-xs font-mono uppercase tracking-widest mb-3">
        Select Cluster ({clusters.length} found)
      </p>
      <div className="flex flex-wrap gap-2">
        {clusters.map((cluster) => (
          <button
            key={cluster.name}
            onClick={() => onSelect(selected === cluster.name ? null : cluster.name)}
            className={`
              flex items-center gap-2 px-4 py-2 rounded-lg border font-mono text-sm
              transition-all duration-150
              ${selected === cluster.name
                ? 'border-terminal-accent bg-terminal-accent/10 text-terminal-accent glow-accent'
                : 'border-terminal-border bg-terminal-card text-terminal-dim hover:border-terminal-accent/50 hover:text-terminal-text'
              }
            `}
          >
            <span className={`status-dot ${cluster.is_current ? 'healthy' : 'warning'}`} />
            <span>{cluster.name}</span>
            {cluster.is_current && (
              <span className="text-xs text-terminal-green">(current)</span>
            )}
          </button>
        ))}
      </div>
      {!selected && (
        <p className="text-terminal-dim text-xs font-mono mt-2">
          No cluster selected — will use default context
        </p>
      )}
    </div>
  )
}
