import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import LoadingSpinner from '../components/LoadingSpinner'
import { getCandidates, getAnalytics } from '../api/client'
import { Users, Briefcase, BarChart3, UserSearch } from 'lucide-react'

export default function RecruiterDashboard() {
  const [stats, setStats] = useState({ candidates: 0, jobs: 0 })
  const [recentCandidates, setRecentCandidates] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getCandidates({ page_size: 5 }), getAnalytics()])
      .then(([candidatesRes, analyticsRes]) => {
        setStats({
          candidates: analyticsRes.data.total_candidates,
          jobs: analyticsRes.data.total_jobs,
        })
        setRecentCandidates(candidatesRes.data)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Layout><LoadingSpinner text="Loading dashboard..." /></Layout>

  return (
    <Layout>
      <div className="space-y-8 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold">Recruiter Dashboard</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Overview of your hiring pipeline
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard icon={Users} label="Total Candidates" value={stats.candidates} color="primary" />
          <Link to="/jobs" className="block">
            <StatCard icon={Briefcase} label="Active Jobs" value={stats.jobs} color="green" clickable />
          </Link>
          <Link to="/rank" className="block">
            <StatCard icon={UserSearch} label="Rank Candidates" value="→" color="purple" clickable />
          </Link>
          <Link to="/analytics" className="block">
            <StatCard icon={BarChart3} label="View Analytics" value="→" color="orange" clickable />
          </Link>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Recent Candidates</h2>
            <Link to="/candidates" className="text-sm text-primary-600 hover:underline">
              View all
            </Link>
          </div>
          {recentCandidates.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No candidates yet</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Name</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Skills</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Resumes</th>
                  </tr>
                </thead>
                <tbody>
                  {recentCandidates.map((c) => (
                    <tr key={c.id} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                      <td className="py-3 px-2">
                        <Link to={`/candidate/${c.id}`} className="text-primary-600 hover:underline font-medium">
                          {c.name || 'Unknown'}
                        </Link>
                      </td>
                      <td className="py-3 px-2 text-gray-500 truncate max-w-xs">
                        {c.skills ? (c.skills.length > 60 ? c.skills.slice(0, 60) + '…' : c.skills) : '—'}
                      </td>
                      <td className="py-3 px-2">{c.resume_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

function StatCard({ icon: Icon, label, value, color, clickable }) {
  const colors = {
    primary: 'bg-primary-100 dark:bg-primary-900/30 text-primary-600',
    green: 'bg-green-100 dark:bg-green-900/30 text-green-600',
    purple: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600',
    orange: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600',
  }

  return (
    <div className={`stat-card ${clickable ? 'hover:border-primary-300 dark:hover:border-primary-700 cursor-pointer' : ''}`}>
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
