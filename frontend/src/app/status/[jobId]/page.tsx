'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Download, CheckCircle, XCircle, Loader2, ArrowLeft, ExternalLink } from 'lucide-react'
import ProgressTracker from '@/components/ProgressTracker'

interface JobStatus {
    job_id: string
    status: string
    state: string
    meta: {
        status?: string
    }
    result: {
        status?: string
        s3_url?: string
        repo_name?: string
        analysis?: {
            total_files: number
            code_files: number
            languages: Record<string, number>
            frameworks: string[]
        }
        error?: string
    }
}

export default function StatusPage() {
    const params = useParams()
    const router = useRouter()
    const jobId = params.jobId as string

    const [status, setStatus] = useState<JobStatus | null>(null)
    const [error, setError] = useState('')
    const [polling, setPolling] = useState(true)

    useEffect(() => {
        if (!jobId) return

        const fetchStatus = async () => {
            try {
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/status/${jobId}`)

                if (!response.ok) {
                    throw new Error('Failed to fetch status')
                }

                const data = await response.json()
                setStatus(data)

                // Stop polling if job is completed or failed
                if (data.state === 'SUCCESS' || data.state === 'FAILURE') {
                    setPolling(false)

                    // Fetch final result
                    if (data.state === 'SUCCESS') {
                        const resultResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/result/${jobId}`)
                        const resultData = await resultResponse.json()
                        setStatus(prev => prev ? { ...prev, result: resultData } : null)
                    }
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to fetch status')
                setPolling(false)
            }
        }

        fetchStatus()

        // Poll every 2 seconds while job is running
        const interval = polling ? setInterval(fetchStatus, 2000) : null

        return () => {
            if (interval) clearInterval(interval)
        }
    }, [jobId, polling])

    const getCurrentStage = () => {
        if (!status) return 'PENDING'
        if (status.state === 'SUCCESS') return 'SUCCESS'
        if (status.state === 'FAILURE') return 'FAILURE'
        return status.state || 'PENDING'
    }

    return (
        <main className="min-h-screen relative overflow-hidden">
            {/* Background */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse-slow" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }} />
            </div>

            <div className="relative z-10 container mx-auto px-4 py-16">
                {/* Back button */}
                <motion.button
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    onClick={() => router.push('/')}
                    className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8"
                >
                    <ArrowLeft className="w-5 h-5" />
                    Back to Home
                </motion.button>

                <div className="max-w-3xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="glass rounded-2xl p-8 md:p-12 shadow-2xl"
                    >
                        {/* Header */}
                        <div className="text-center mb-8">
                            <h1 className="text-3xl font-bold mb-2">Documentation Generation</h1>
                            <p className="text-gray-400">Job ID: <code className="text-cyan-400">{jobId}</code></p>
                        </div>

                        {/* Error State */}
                        {error && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="bg-red-500/10 border border-red-500/50 rounded-xl p-6 mb-6 flex items-start gap-4"
                            >
                                <XCircle className="w-6 h-6 text-red-400 flex-shrink-0 mt-1" />
                                <div>
                                    <h3 className="font-semibold text-red-400 mb-1">Error</h3>
                                    <p className="text-gray-300">{error}</p>
                                </div>
                            </motion.div>
                        )}

                        {/* Progress Tracker */}
                        {status && !error && (
                            <div className="mb-8">
                                <ProgressTracker currentStage={getCurrentStage()} />
                            </div>
                        )}

                        {/* Success State */}
                        {status?.state === 'SUCCESS' && status.result?.s3_url && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="bg-green-500/10 border border-green-500/50 rounded-xl p-6 mb-6"
                            >
                                <div className="flex items-start gap-4 mb-4">
                                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
                                    <div className="flex-1">
                                        <h3 className="font-semibold text-green-400 mb-1">Documentation Generated!</h3>
                                        <p className="text-gray-300 mb-4">
                                            Your documentation for <strong>{status.result.repo_name}</strong> is ready.
                                        </p>

                                        {/* Analysis Summary */}
                                        {status.result.analysis && (
                                            <div className="glass rounded-lg p-4 mb-4 space-y-2 text-sm">
                                                <p><strong>Total Files:</strong> {status.result.analysis.total_files}</p>
                                                <p><strong>Code Files:</strong> {status.result.analysis.code_files}</p>
                                                <p><strong>Languages:</strong> {Object.keys(status.result.analysis.languages).join(', ')}</p>
                                                {status.result.analysis.frameworks.length > 0 && (
                                                    <p><strong>Frameworks:</strong> {status.result.analysis.frameworks.join(', ')}</p>
                                                )}
                                            </div>
                                        )}

                                        {/* Download Button */}
                                        <a
                                            href={status.result.s3_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 rounded-xl font-semibold text-white shadow-lg transition-all"
                                        >
                                            <Download className="w-5 h-5" />
                                            View Documentation
                                            <ExternalLink className="w-4 h-4" />
                                        </a>
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        {/* Failure State */}
                        {status?.state === 'FAILURE' && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="bg-red-500/10 border border-red-500/50 rounded-xl p-6"
                            >
                                <div className="flex items-start gap-4">
                                    <XCircle className="w-6 h-6 text-red-400 flex-shrink-0 mt-1" />
                                    <div>
                                        <h3 className="font-semibold text-red-400 mb-1">Generation Failed</h3>
                                        <p className="text-gray-300">
                                            {status.result?.error || 'An error occurred during documentation generation.'}
                                        </p>
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        {/* Loading State */}
                        {polling && !error && (
                            <div className="text-center text-gray-400">
                                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-cyan-400" />
                                <p>Processing your repository...</p>
                                <p className="text-sm mt-2">This may take a few minutes depending on the repository size.</p>
                            </div>
                        )}
                    </motion.div>
                </div>
            </div>
        </main>
    )
}
