import type { Metadata } from 'next'
import './globals.css'
import { QueryProvider } from '@/components/QueryProvider'

export const metadata: Metadata = {
  title: 'AI Kubernetes Agent',
  description: 'AI-powered Kubernetes troubleshooting',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <QueryProvider>
          {children}
        </QueryProvider>
      </body>
    </html>
  )
}
