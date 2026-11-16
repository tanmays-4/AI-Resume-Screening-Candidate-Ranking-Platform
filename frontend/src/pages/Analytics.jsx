import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import LoadingSpinner from '../components/LoadingSpinner'
import { getAnalytics } from '../api/client'
import { getErrorMessage } from '../utils/errors'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import { Users, Briefcase, Target, Award } from 'lucide-react'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1']

export default function Analytics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getAnalytics()
      .then(({ data }) => setData(data))
      .catch((err) => setError(getErrorMessage(err, 'Failed to load analytics')))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Layout><LoadingSpinner text="Loading analytics..." /></Layout>

  return (
    <Layout>
      <div className="space-y-8 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Hiring pipeline insights and metrics</p>
        </div>

        {error && (
          <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-sm">{error}</div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard icon={Users} label="Total Candidates" value={data?.total_candidates || 0} color="primary" />
          <MetricCard icon={Briefcase} label="Total Jobs" value={data?.total_jobs || 0} color="green" />
          <MetricCard icon={Target} label="Avg Match Score" value={`${data?.avg_match_score || 0}%`} color="purple" />
          <MetricCard icon={Award} label="Avg ATS Score" value={`${data?.avg_ats_score || 0}%`} color="orange" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="font-semibold mb-4">Top Skills Distribution</h2>
            {data?.skills_distribution?.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={data.skills_distribution}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  >
                    {data.skills_distribution.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-gray-500 py-12">No skill data available</p>
            )}
          </div>

          <div className="card">
            <h2 className="font-semibold mb-4">Match Score Distribution</h2>
            {data?.score_distribution?.some((b) => b.value > 0) ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data.score_distribution}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-gray-500 py-12">No scores yet — rank candidates against a job first</p>
            )}
          </div>
        </div>

        {data?.top_candidates?.length > 0 && (
          <div className="card">
            <h2 className="font-semibold mb-4">Top Candidates by Match Score</h2>
            <div className="space-y-3">
              {data.top_candidates.map((c, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <div className="flex items-center gap-3">
                    <span className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-sm font-bold text-primary-700">
                      {i + 1}
                    </span>
                    <span className="font-medium">{c.name}</span>
                  </div>
                  <div className="flex gap-3 text-sm">
                    <span className="text-primary-600">Match: {c.match_score}%</span>
                    <span className="text-green-600">ATS: {c.ats_score}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

function MetricCard({ icon: Icon, label, value, color }) {
  const colors = {
    primary: 'bg-primary-100 dark:bg-primary-900/30 text-primary-600',
    green: 'bg-green-100 dark:bg-green-900/30 text-green-600',
    purple: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600',
    orange: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600',
  }

  return (
    <div className="stat-card">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${colors[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
      </div>
    </div>
  )
}
