'use client'

import { motion } from 'framer-motion'
import { CheckCircle2, Circle, Loader2 } from 'lucide-react'

interface Stage {
    id: string
    label: string
    status: 'pending' | 'active' | 'completed'
}

interface ProgressTrackerProps {
    currentStage: string
}

export default function ProgressTracker({ currentStage }: ProgressTrackerProps) {
    const stages: Stage[] = [
        { id: 'PENDING', label: 'Queued', status: 'pending' },
        { id: 'CLONING', label: 'Cloning Repository', status: 'pending' },
        { id: 'ANALYZING', label: 'Analyzing Code', status: 'pending' },
        { id: 'GENERATING', label: 'Generating Docs', status: 'pending' },
        { id: 'UPLOADING', label: 'Uploading Results', status: 'pending' },
        { id: 'SUCCESS', label: 'Completed', status: 'pending' },
    ]

    // Update stage statuses based on current stage
    const currentIndex = stages.findIndex(s => s.id === currentStage)
    const updatedStages = stages.map((stage, index) => {
        if (currentStage === 'SUCCESS') {
            return { ...stage, status: 'completed' }
        }
        return {
            ...stage,
            status: index < currentIndex ? 'completed' : index === currentIndex ? 'active' : 'pending'
        }
    }) as Stage[]

    return (
        <div className="space-y-4">
            {updatedStages.map((stage, index) => (
                <motion.div
                    key={stage.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center gap-4"
                >
                    <div className="flex-shrink-0">
                        {stage.status === 'completed' && (
                            <CheckCircle2 className="w-6 h-6 text-green-400" />
                        )}
                        {stage.status === 'active' && (
                            <Loader2 className="w-6 h-6 text-cyan-400 animate-spin" />
                        )}
                        {stage.status === 'pending' && (
                            <Circle className="w-6 h-6 text-gray-600" />
                        )}
                    </div>

                    <div className="flex-1">
                        <p className={`font-medium ${stage.status === 'completed' ? 'text-green-400' :
                            stage.status === 'active' ? 'text-cyan-400' :
                                'text-gray-500'
                            }`}>
                            {stage.label}
                        </p>
                    </div>

                    {stage.status === 'active' && (
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: '100%' }}
                            transition={{ duration: 2, repeat: Infinity }}
                            className="absolute bottom-0 left-0 h-0.5 bg-gradient-to-r from-cyan-500 to-blue-500"
                        />
                    )}
                </motion.div>
            ))}
        </div>
    )
}
