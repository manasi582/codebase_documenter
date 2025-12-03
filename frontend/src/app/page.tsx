'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Github, Sparkles } from 'lucide-react'
import URLInput from '@/components/URLInput'

export default function Home() {
    const router = useRouter()
    const [isSubmitting, setIsSubmitting] = useState(false)

    const handleSubmit = async (githubUrl: string) => {
        setIsSubmitting(true)

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ github_url: githubUrl }),
            })

            if (!response.ok) {
                const error = await response.json()
                throw new Error(error.detail || 'Failed to submit repository')
            }

            const data = await response.json()
            router.push(`/status/${data.job_id}`)
        } catch (error) {
            console.error('Error:', error)
            alert(error instanceof Error ? error.message : 'Failed to submit repository')
            setIsSubmitting(false)
        }
    }

    return (
        <main className="min-h-screen relative overflow-hidden">
            {/* Animated background elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse-slow" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }} />
            </div>

            <div className="relative z-10 container mx-auto px-4 py-16">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <div className="flex items-center justify-center gap-3 mb-6">
                        <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                        >
                            <Sparkles className="w-12 h-12 text-cyan-400" />
                        </motion.div>
                        <h1 className="text-6xl font-bold gradient-text">
                            Codebase Documenter
                        </h1>
                    </div>
                    <p className="text-xl text-gray-300 max-w-2xl mx-auto">
                        Automate Documentation. Accelerate Development.
                    </p>
                </motion.div>

                {/* Main Input Section */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="max-w-3xl mx-auto"
                >
                    <div className="glass rounded-2xl p-8 md:p-12 shadow-2xl">
                        <div className="flex items-center gap-3 mb-6">
                            <Github className="w-8 h-8 text-cyan-400" />
                            <h2 className="text-2xl font-semibold">Enter GitHub Repository</h2>
                        </div>

                        <URLInput onSubmit={handleSubmit} isLoading={isSubmitting} />
                    </div>
                </motion.div>

                {/* About Section */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                    className="mt-16 text-center max-w-2xl mx-auto"
                >
                    <p className="text-gray-400 text-sm">
                        An AI-powered tool that automatically generates comprehensive documentation for any GitHub repository.
                        Simply paste a repository URL and get professional READMEs, setup guides, and code documentation in minutes.
                    </p>
                </motion.div>
            </div>
        </main>
    )
}
