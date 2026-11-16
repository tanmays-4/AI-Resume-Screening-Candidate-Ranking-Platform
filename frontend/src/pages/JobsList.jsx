import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import LoadingSpinner from '../components/LoadingSpinner'
import { getJobs, deleteJob } from '../api/client'
import { getErrorMessage } from '../utils/errors'
import { Briefcase, MapPin, Clock, Plus, Trash2, UserSearch } from 'lucide-react'

export default function JobsList() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expanded, setExpanded] = useState(null)

  const fetchJobs = () => {
    setLoading(true)
    getJobs()
      .then(({ data }) => setJobs(data))
      .catch((err) => setError(getErrorMessage(err, 'Failed to load jobs')))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchJobs() }, [])

  const handleDelete = async (job) => {
    if (!confirm(`Delete job "${job.title}" and all its scores? This cannot be undone.`)) return
    try {
      await deleteJob(job.id)
      setJobs((prev) => prev.filter((j) => j.id !== job.id))
    } catch (err) {
      alert(getErrorMessage(err, 'Delete failed'))
    }
  }

  return (
    <Layout>
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold">Job Descriptions</h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">Manage open roles and rank candidates against them</p>
          </div>
          <Link to="/create-job" className="btn-primary flex items-center gap-2 self-start">
            <Plus className="w-4 h-4" /> New Job
          </Link>
        </div>

        {error && (
          <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-sm">{error}</div>
        )}

        {loading ? (
          <LoadingSpinner text="Loading jobs..." />
        ) : jobs.length === 0 ? (
          <div className="card text-center py-12">
            <Briefcase className="w-12 h-12 mx-auto text-gray-400 mb-3" />
            <p className="font-medium">No jobs yet</p>
            <p className="text-sm text-gray-500 mt-1">Create your first job description to start screening.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {jobs.map((job) => (
              <div key={job.id} className="card flex flex-col gap-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold">{job.title}</h2>
                    <div className="flex flex-wrap gap-3 mt-1 text-xs text-gray-500">
                      {job.location && <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{job.location}</span>}
                      {job.experience && <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" />{job.experience}</span>}
                      <span>Posted {new Date(job.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(job)}
                    className="p-1.5 rounded hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600"
                    aria-label="Delete job"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <p className={`text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap ${expanded === job.id ? '' : 'line-clamp-3'}`}>
                  {job.description}
                </p>
                {job.description.length > 200 && (
                  <button
                    onClick={() => setExpanded(expanded === job.id ? null : job.id)}
                    className="text-xs text-primary-600 hover:underline self-start"
                  >
                    {expanded === job.id ? 'Show less' : 'Show more'}
                  </button>
                )}

                <div className="flex flex-wrap gap-2">
                  {job.required_skills.split(',').map((s) => s.trim()).filter(Boolean).map((s) => (
                    <span key={s} className="px-2.5 py-0.5 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 rounded-full text-xs">
                      {s}
                    </span>
                  ))}
                </div>

                <Link to={`/rank?job=${job.id}`} className="btn-secondary flex items-center justify-center gap-2 mt-auto text-sm">
                  <UserSearch className="w-4 h-4" /> Rank candidates for this job
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}
