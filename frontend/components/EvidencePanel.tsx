'use client'

import { useState } from 'react'

interface EvidencePanelProps {
  evidence: Record<string, any>
}

type Tab = 'pods' | 'events' | 'deployments' | 'network'

const TABS: { key: Tab; label: string; emoji: string }[] = [
  { key: 'pods', label: 'Pods', emoji: '📦' },
  { key: 'events', label: 'Events', emoji: '⚡' },
  { key: 'deployments', label: 'Deployments', emoji: '🚀' },
  { key: 'network', label: 'Network', emoji: '🌐' },
]

function PodSummary({ pods }: { pods: any }) {
  if (pods?.error) return <ErrorBox msg={pods.error} />
  return (
    <div className="space-y-3">
      <div className="flex gap-4">
        <Stat label="Total" value={pods?.total_pods ?? '—'} />
        <Stat label="Problems" value={pods?.problematic_count ?? 0} color="red" />
      </div>
      {pods?.problematic_pods?.length > 0 ? (
        <div className="space-y-1.5">
          {pods.problematic_pods.map((p: any, i: number) => (
            <div key={i} className="p-2 rounded bg-terminal-bg border border-terminal-red/20">
              <span className="text-terminal-red font-mono text-xs">{p.namespace}/{p.name}</span>
              <span className="ml-2 text-terminal-yellow text-xs font-mono">{p.status}</span>
              {p.restart_count > 0 && (
                <span className="ml-2 text-terminal-dim text-xs font-mono">restarts: {p.restart_count}</span>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-terminal-green text-sm font-mono">All pods healthy ✓</p>
      )}
    </div>
  )
}

function EventsSummary({ events }: { events: any }) {
  if (events?.error) return <ErrorBox msg={events.error} />
  return (
    <div className="space-y-3">
      <div className="flex gap-4">
        <Stat label="Total" value={events?.total_events ?? '—'} />
        <Stat label="Critical" value={events?.critical_count ?? 0} color="red" />
      </div>
      {events?.critical_events?.length > 0 ? (
        <div className="space-y-1.5 max-h-64 overflow-y-auto">
          {events.critical_events.slice(0, 10).map((e: any, i: number) => (
            <div key={i} className="p-2 rounded bg-terminal-bg border border-terminal-yellow/20 text-xs font-mono">
              <span className="text-terminal-yellow">{e.reason}</span>
              <span className="text-terminal-dim ml-2">{e.object}</span>
              <p className="text-terminal-dim mt-0.5 text-xs truncate">{e.message}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-terminal-green text-sm font-mono">No critical events ✓</p>
      )}
    </div>
  )
}

function DeploymentSummary({ deployments }: { deployments: any }) {
  if (deployments?.error) return <ErrorBox msg={deployments.error} />
  return (
    <div className="space-y-3">
      <div className="flex gap-4">
        <Stat label="Total" value={deployments?.total_deployments ?? '—'} />
        <Stat label="Unhealthy" value={deployments?.unhealthy_count ?? 0} color="red" />
      </div>
      {deployments?.unhealthy_deployments?.length > 0 ? (
        <div className="space-y-1.5">
          {deployments.unhealthy_deployments.map((d: any, i: number) => (
            <div key={i} className="p-2 rounded bg-terminal-bg border border-terminal-red/20 text-xs font-mono">
              <span className="text-terminal-red">{d.namespace}/{d.name}</span>
              <span className="ml-2 text-terminal-dim">
                {d.available_replicas}/{d.desired_replicas} ready
              </span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-terminal-green text-sm font-mono">All deployments healthy ✓</p>
      )}
    </div>
  )
}

function NetworkSummary({ network }: { network: any }) {
  if (network?.error) return <ErrorBox msg={network.error} />
  return (
    <div className="space-y-3">
      <div className="flex gap-4">
        <Stat label="Services" value={network?.total_services ?? '—'} />
        <Stat label="Issues" value={network?.issue_count ?? 0} color="red" />
      </div>
      {network?.issues?.length > 0 ? (
        <div className="space-y-1.5">
          {network.issues.map((issue: any, i: number) => (
            <div key={i} className="p-2 rounded bg-terminal-bg border border-terminal-red/20 text-xs font-mono">
              <span className={issue.severity === 'critical' ? 'text-terminal-red' : 'text-terminal-yellow'}>
                {issue.service}
              </span>
              <p className="text-terminal-dim mt-0.5">{issue.issue}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-terminal-green text-sm font-mono">No network issues ✓</p>
      )}
    </div>
  )
}

function Stat({ label, value, color }: { label: string; value: any; color?: string }) {
  return (
    <div>
      <p className="text-terminal-dim text-xs font-mono">{label}</p>
      <p className={`font-mono font-semibold text-lg ${color === 'red' && Number(value) > 0 ? 'text-terminal-red' : 'text-terminal-text'}`}>
        {value}
      </p>
    </div>
  )
}

function ErrorBox({ msg }: { msg: string }) {
  return (
    <div className="p-3 rounded bg-terminal-red/5 border border-terminal-red/20">
      <p className="text-terminal-red text-xs font-mono">{msg}</p>
    </div>
  )
}

export function EvidencePanel({ evidence }: EvidencePanelProps) {
  const [tab, setTab] = useState<Tab>('pods')

  return (
    <div className="rounded-lg border border-terminal-border bg-terminal-card overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-terminal-border">
        <span className="text-terminal-dim text-xs font-mono uppercase tracking-widest">
          Investigation Evidence
        </span>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-terminal-border">
        {TABS.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`
              flex-1 px-3 py-3 text-xs font-mono transition-colors
              ${tab === t.key
                ? 'text-terminal-accent border-b-2 border-terminal-accent bg-terminal-accent/5'
                : 'text-terminal-dim hover:text-terminal-text'
              }
            `}
          >
            <span className="mr-1">{t.emoji}</span>
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="p-5">
        {tab === 'pods' && <PodSummary pods={evidence?.pods} />}
        {tab === 'events' && <EventsSummary events={evidence?.events} />}
        {tab === 'deployments' && <DeploymentSummary deployments={evidence?.deployments} />}
        {tab === 'network' && <NetworkSummary network={evidence?.network} />}
      </div>
    </div>
  )
}
