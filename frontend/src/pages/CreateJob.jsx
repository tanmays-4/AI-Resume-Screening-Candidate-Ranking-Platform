import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { createJob } from '../api/client'
import { Briefcase, MapPin, Clock, Code, CheckCircle } from 'lucide-react'
import { getErrorMessage } from '../utils/errors'

export default function CreateJob() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    title: '',
    description: '',
    required_skills: '',
    experience: '',
    location: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await createJob(form)
      setSuccess(true)
      setTimeout(() => navigate(`/rank?job=${data.id}`), 1500)
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to create job'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout>
      <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold">Create Job Description</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Define requirements for AI-powered candidate screening
          </p>
        </div>

        {error && (
          <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-sm">
            {error}
          </div>
        )}

        {success && (
          <div className="flex items-center gap-2 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400">
            <CheckCircle className="w-5 h-5" />
            Job created! Redirecting to ranking...
          </div>
        )}

        <form onSubmit={handleSubmit} className="card space-y-5">
          <div>
            <label className="block text-sm font-medium mb-1.5">Job Title</label>
            <div className="relative">
              <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                required
                className="input-field pl-10"
                placeholder="Senior Software Engineer"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Description</label>
            <textarea
              required
              minLength={10}
              rows={5}
              className="input-field resize-none"
              placeholder="Describe the role, responsibilities, and expectations..."
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Required Skills (comma-separated)</label>
            <div className="relative">
              <Code className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <textarea
                required
                rows={2}
                className="input-field pl-10 resize-none"
                placeholder="Python, React, PostgreSQL, Docker, AWS"
                value={form.required_skills}
                onChange={(e) => setForm({ ...form, required_skills: e.target.value })}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Experience Required</label>
              <div className="relative">
                <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  className="input-field pl-10"
                  placeholder="3-5 years"
                  value={form.experience}
                  onChange={(e) => setForm({ ...form, experience: e.target.value })}
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Location</label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  className="input-field pl-10"
                  placeholder="Remote / New York, NY"
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                />
              </div>
            </div>
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full py-3">
            {loading ? 'Creating...' : 'Create Job Description'}
          </button>
        </form>
      </div>
    </Layout>
  )
}
