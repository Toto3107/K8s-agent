'use client'

import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

const API = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export function useClusters() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['clusters'],
    queryFn: async () => {
      const res = await axios.get(`${API}/clusters`)
      return res.data.clusters || []
    },
    staleTime: 60_000,
    retry: 2,
  })

  return {
    clusters: data || [],
    isLoading,
    error
  }
}
