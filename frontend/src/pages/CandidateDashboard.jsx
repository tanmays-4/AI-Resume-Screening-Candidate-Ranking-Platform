import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import LoadingSpinner from '../components/LoadingSpinner'
import { getMyProfile } from '../api/client'
import { Upload, FileText, User, Phone, GraduationCap, Briefcase } from 'lucide-react'
import { getErrorMessage } from '../utils/errors'

export default function CandidateDashboard() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getMyProfile()
      .then(({ data }) => setProfile(data))
      .catch((err) => setError(getErrorMessage(err, 'Failed to load profile')))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Layout><LoadingSpinner text="Loading dashboard..." /></Layout>

  return (
    <Layout>
      <div className="space-y-8 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold">Candidate Dashboard</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Manage your resume and track your profile
          </p>
        </div>

        {error && (
          <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="stat-card">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                <FileText className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Resumes Uploaded</p>
                <p className="text-2xl font-bold">{profile?.resume_count || 0}</p>
              </div>
            </div>
          </div>

          <div className="stat-card">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <User className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Profile Status</p>
                <p className="text-2xl font-bold">
                  {profile?.skills ? 'Complete' : 'Incomplete'}
                </p>
              </div>
            </div>
          </div>

          <Link to="/upload" className="stat-card hover:border-primary-300 dark:hover:border-primary-700 transition-colors cursor-pointer">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <Upload className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Quick Action</p>
                <p className="text-lg font-semibold text-primary-600">Upload Resume</p>
              </div>
            </div>
          </Link>
        </div>

        {profile && (
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Profile Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InfoItem icon={User} label="Name" value={profile.name || 'Not set'} />
              <InfoItem icon={Phone} label="Phone" value={profile.phone || 'Not set'} />
              <InfoItem icon={GraduationCap} label="Education" value={profile.education || 'Not extracted'} />
              <InfoItem icon={Briefcase} label="Experience" value={profile.experience ? (profile.experience.length > 100 ? profile.experience.slice(0, 100) + '…' : profile.experience) : 'Not extracted'} />
            </div>
            {profile.skills && (
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-500 mb-2">Skills</p>
                <div className="flex flex-wrap gap-2">
                  {profile.skills.split(',').filter((s) => s.trim()).map((skill, i) => (
                    <span key={i} className="px-3 py-1 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 rounded-full text-sm">
                      {skill.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}

function InfoItem({ icon: Icon, label, value }) {
  return (
    <div className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
      <Icon className="w-5 h-5 text-gray-400 mt-0.5" />
      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
        <p className="text-sm mt-0.5">{value}</p>
      </div>
    </div>
  )
}
