'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Github, ArrowRight, Loader2 } from 'lucide-react'

interface URLInputProps {
    onSubmit: (url: string) => void
    isLoading?: boolean
}

export default function URLInput({ onSubmit, isLoading = false }: URLInputProps) {
    const [url, setUrl] = useState('')
    const [error, setError] = useState('')

    const validateGitHubUrl = (url: string): boolean => {
        const patterns = [
            /^https:\/\/github\.com\/[\w-]+\/[\w.-]+\/?$/,
            /^git@github\.com:[\w-]+\/[\w.-]+\.git$/,
        ]
        return patterns.some(pattern => pattern.test(url.trim()))
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        if (!url.trim()) {
            setError('Please enter a GitHub URL')
            return
        }

        if (!validateGitHubUrl(url)) {
            setError('Please enter a valid GitHub repository URL')
            return
        }

        onSubmit(url.trim())
    }

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Github className="w-5 h-5 text-gray-400" />
                </div>
                <input
                    type="text"
                    value={url}
                    onChange={(e) => {
                        setUrl(e.target.value)
                        setError('')
                    }}
                    placeholder="https://github.com/username/repository"
                    className="w-full pl-12 pr-4 py-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                    disabled={isLoading}
                />
            </div>

            {error && (
                <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-red-400 text-sm"
                >
                    {error}
                </motion.p>
            )}

            <motion.button
                type="submit"
                disabled={isLoading}
                whileHover={{ scale: isLoading ? 1 : 1.02 }}
                whileTap={{ scale: isLoading ? 1 : 0.98 }}
                className="w-full py-4 px-6 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 rounded-xl font-semibold text-white shadow-lg shadow-cyan-500/50 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isLoading ? (
                    <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Analyzing Repository...
                    </>
                ) : (
                    <>
                        Generate Documentation
                        <ArrowRight className="w-5 h-5" />
                    </>
                )}
            </motion.button>
        </form>
    )
}
