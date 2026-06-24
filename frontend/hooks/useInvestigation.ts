'use client'

import { useState } from 'react'
import axios from 'axios'

const API = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

interface Step {
  label: string
  status: 'pending' | 'running' | 'done' | 'error'
}

const INVESTIGATION_STEPS: string[] = [
  'Checking Pods',
  'Reading Logs',
  'Analyzing Events',
  'Inspecting Deployments',
  'Checking Networking',
  'AI Reasoning',
  'Root Cause Analysis Complete',
]

export function useInvestigation() {
  const [isInvestigating, setIsInvestigating] = useState(false)
  const [steps, setSteps] = useState<Step[]>([])
  const [diagnosis, setDiagnosis] = useState<any>(null)
  const [evidence, setEvidence] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const setStepStatus = (index: number, status: Step['status']) => {
    setSteps(prev => prev.map((s, i) => i === index ? { ...s, status } : s))
  }

  const investigate = async (context: string | null) => {
    setIsInvestigating(true)
    setError(null)
    setDiagnosis(null)
    setEvidence(null)

    // Init all steps as pending
    setSteps(INVESTIGATION_STEPS.map(label => ({ label, status: 'pending' })))

    // Animate steps while waiting for backend
    const stepTimers: NodeJS.Timeout[] = []

    // Start animating steps with delays (estimated timing)
    const delays = [0, 1200, 2500, 4000, 5200, 6500, 0]
    delays.slice(0, -1).forEach((delay, i) => {
      const t = setTimeout(() => {
        setStepStatus(i, 'running')
        if (i > 0) setStepStatus(i - 1, 'done')
      }, delay)
      stepTimers.push(t)
    })

    try {
      const params = context ? `?context=${encodeURIComponent(context)}` : ''
      const res = await axios.post(`${API}/investigate${params}`, {}, {
        timeout: 120_000
      })

      const data = res.data

      // Mark all investigation steps done, start AI
      setSteps(prev => prev.map((s, i) =>
        i < 5 ? { ...s, status: 'done' }
          : i === 5 ? { ...s, status: 'done' }
            : { ...s, status: 'done' }
      ))

      setDiagnosis(data.diagnosis)
      setEvidence(data.investigation)

    } catch (err: any) {
      // Mark running step as error
      setSteps(prev => prev.map(s =>
        s.status === 'running' ? { ...s, status: 'error' } : s
      ))

      const msg =
        err?.response?.data?.detail?.message ||
        err?.response?.data?.detail ||
        err?.message ||
        'Unknown error occurred'

      setError(msg)
    } finally {
      stepTimers.forEach(clearTimeout)
      setIsInvestigating(false)
    }
  }

  const reset = () => {
    setDiagnosis(null)
    setEvidence(null)
    setError(null)
    setSteps([])
  }

  return { investigate, isInvestigating, steps, diagnosis, evidence, error, reset }
}
