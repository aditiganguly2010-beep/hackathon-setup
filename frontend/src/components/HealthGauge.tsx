import { getHealthScoreBgColor, getHealthScoreColor } from '../lib/utils'

interface HealthGaugeProps {
  score: number
}

export default function HealthGauge({ score }: HealthGaugeProps) {
  const circumference = 2 * Math.PI * 45
  const offset = circumference - (score / 100) * circumference

  return (
    <div className="relative w-32 h-32">
      <svg className="w-full h-full transform -rotate-90">
        {/* Background circle */}
        <circle
          cx="64"
          cy="64"
          r="45"
          stroke="#e5e7eb"
          strokeWidth="8"
          fill="none"
        />
        {/* Progress circle */}
        <circle
          cx="64"
          cy="64"
          r="45"
          stroke={score >= 80 ? '#22c55e' : score >= 60 ? '#f59e0b' : '#ef4444'}
          strokeWidth="8"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-500 ease-in-out"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className={`text-3xl font-bold ${getHealthScoreColor(score)}`}>
          {score}
        </span>
      </div>
    </div>
  )
}
