'use client'

import { useState } from 'react'
import { ClusterSelector } from '@/components/ClusterSelector'
import { InvestigationPanel } from '@/components/InvestigationPanel'
import { DiagnosisCard } from '@/components/DiagnosisCard'
import { EvidencePanel } from '@/components/EvidencePanel'
import { Header } from '@/components/Header'
import { useInvestigation } from '@/hooks/useInvestigation'
import { useClusters } from '@/hooks/useClusters'

export default function Home() {
  const [selectedContext, setSelectedContext] = useState<string | null>(null)
  const { clusters, isLoading: clustersLoading } = useClusters()
  const {
    investigate,
    isInvestigating,
    steps,
    diagnosis,
    evidence,
    error,
    reset
  } = useInvestigation()

  const handleInvestigate = () => {
    investigate(selectedContext)
  }

  return (
    <div className="min-h-screen bg-terminal-bg grid-bg">
      {/* Scan line effect */}
      <div className="scan-line" />

      <div className="max-w-6xl mx-auto px-4 py-8">
        <Header />

        {/* Cluster Selector */}
        <div className="mt-8">
          <ClusterSelector
            clusters={clusters}
            isLoading={clustersLoading}
            selected={selectedContext}
            onSelect={setSelectedContext}
          />
        </div>

        {/* Investigate Button */}
        <div className="mt-6 flex items-center gap-4">
          <button
            onClick={handleInvestigate}
            disabled={isInvestigating}
            className={`
              relative px-8 py-4 rounded-lg font-mono font-semibold text-sm tracking-widest uppercase
              transition-all duration-200
              ${isInvestigating
                ? 'bg-terminal-card border border-terminal-border text-terminal-dim cursor-not-allowed'
                : 'bg-terminal-accent/10 border border-terminal-accent text-terminal-accent hover:bg-terminal-accent/20 glow-accent cursor-pointer'
              }
            `}
          >
            {isInvestigating ? (
              <span className="flex items-center gap-2">
                <span className="inline-block w-2 h-2 rounded-full bg-terminal-accent animate-pulse" />
                Investigating...
              </span>
            ) : (
              '⚡ Investigate Cluster'
            )}
          </button>

          {(diagnosis || error) && (
            <button
              onClick={reset}
              className="px-4 py-4 text-terminal-dim text-sm font-mono hover:text-terminal-text transition-colors"
            >
              ↺ Reset
            </button>
          )}

          {selectedContext && (
            <span className="text-terminal-dim text-sm font-mono">
              ctx: <span className="text-terminal-accent">{selectedContext}</span>
            </span>
          )}
        </div>

        {/* Error State */}
        {error && (
          <div className="mt-6 p-4 rounded-lg border border-terminal-red/40 bg-terminal-red/5 animate-fade-in">
            <p className="text-terminal-red font-mono text-sm font-semibold mb-1">Investigation Failed</p>
            <p className="text-terminal-text text-sm">{error}</p>
            <div className="mt-3 p-3 bg-terminal-card rounded text-terminal-dim text-xs font-mono">
              <p className="mb-1">Verify the following:</p>
              <p>• kubectl is installed and in PATH</p>
              <p>• kubeconfig is valid: <span className="text-terminal-accent">kubectl cluster-info</span></p>
              <p>• KUBECONFIG_PATH is set if using a custom path</p>
            </div>
          </div>
        )}

        {/* Investigation Progress */}
        {(isInvestigating || steps.length > 0) && (
          <div className="mt-6">
            <InvestigationPanel steps={steps} isRunning={isInvestigating} />
          </div>
        )}

        {/* Diagnosis + Evidence */}
        {diagnosis && evidence && (
          <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6 animate-slide-up">
            <DiagnosisCard diagnosis={diagnosis} />
            <EvidencePanel evidence={evidence} />
          </div>
        )}

        {/* Healthy State */}
        {diagnosis && diagnosis.root_cause === 'No issues detected' && (
          <div className="mt-6 p-6 rounded-lg border border-terminal-green/30 bg-terminal-green/5 animate-fade-in text-center">
            <div className="text-4xl mb-3">✅</div>
            <p className="text-terminal-green font-mono font-semibold text-lg">Cluster Healthy</p>
            <p className="text-terminal-dim text-sm mt-1">No critical Kubernetes issues detected.</p>
          </div>
        )}
      </div>
    </div>
  )
}
