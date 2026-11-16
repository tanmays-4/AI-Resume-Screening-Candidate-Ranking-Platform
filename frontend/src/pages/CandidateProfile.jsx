import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout from '../components/Layout'
import LoadingSpinner from '../components/LoadingSpinner'
import ScoreBadge from '../components/ScoreBadge'
import { getCandidate, getMyProfile, downloadResume } from '../api/client'
import { useAuth } from '../context/AuthContext'
import {
  User, Mail, Phone, GraduationCap, Briefcase, FileText, Download, ArrowLeft,
} from 'lucide-react'
import { getErrorMessage } from '../utils/errors'

export default function CandidateProfile() {
  const { id } = useParams()
  const { user } = useAuth()
  const [candidate, setCandidate] = useState(null)
  const [loading, setLoading] = useState(true)
  const [previewText, setPreviewText] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    setError('')
    const fetcher = id ? getCandidate(id) : getMyProfile()
    fetcher
      .then(({ data }) => setCandidate(data))
      .catch((err) => setError(getErrorMessage(err, 'Candidate not found')))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <Layout><LoadingSpinner /></Layout>
  if (!candidate) return <Layout><p className="text-center py-12 text-gray-500">{error || 'Candidate not found'}</p></Layout>

  const isOwnProfile = !id

  const handleDownload = async (resume) => {
    try {
      const { data } = await downloadResume(resume.id)
      const url = window.URL.createObjectURL(data)
      const a = document.createElement('a')
      a.href = url
      a.download = resume.file_name
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      alert(getErrorMessage(err, 'Failed to download resume'))
    }
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
        {!isOwnProfile && user?.role === 'recruiter' && (
          <Link to="/candidates" className="inline-flex items-center gap-1 text-sm text-primary-600 hover:underline">
            <ArrowLeft className="w-4 h-4" /> Back to candidates
          </Link>
        )}

        <div className="card">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
              <User className="w-8 h-8 text-primary-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">{candidate.name || 'Unknown'}</h1>
              <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-500">
                {candidate.email && (
                  <span className="flex items-center gap-1"><Mail className="w-4 h-4" />{candidate.email}</span>
                )}
                {candidate.phone && (
                  <span className="flex items-center gap-1"><Phone className="w-4 h-4" />{candidate.phone}</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {candidate.skills && (
          <div className="card">
            <h2 className="font-semibold mb-3">Skills</h2>
            <div className="flex flex-wrap gap-2">
              {candidate.skills.split(',').filter((s) => s.trim()).map((s, i) => (
                <span key={i} className="px-3 py-1 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 rounded-full text-sm">
                  {s.trim()}
                </span>
              ))}
            </div>
          </div>
        )}

        {candidate.education && (
          <div className="card">
            <h2 className="font-semibold mb-2 flex items-center gap-2">
              <GraduationCap className="w-5 h-5" /> Education
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{candidate.education}</p>
          </div>
        )}

        {candidate.experience && (
          <div className="card">
            <h2 className="font-semibold mb-2 flex items-center gap-2">
              <Briefcase className="w-5 h-5" /> Experience
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{candidate.experience}</p>
          </div>
        )}

        {candidate.scores?.length > 0 && (
          <div className="card">
            <h2 className="font-semibold mb-3">Screening Scores</h2>
            <div className="space-y-2">
              {candidate.scores.map((s) => (
                <div key={s.id} className="flex flex-wrap items-center gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <span className="text-sm font-medium">{s.job_title || `Job #${s.job_id}`}</span>
                  <ScoreBadge score={s.match_score} type="match" />
                  <ScoreBadge score={s.ats_score} type="ats" />
                  {s.missing_skills && (
                    <span className="text-xs text-gray-500">Missing: {s.missing_skills}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {candidate.resumes?.length > 0 && (
          <div className="card">
            <h2 className="font-semibold mb-3 flex items-center gap-2">
              <FileText className="w-5 h-5" /> Resumes ({candidate.resumes.length})
            </h2>
            <div className="space-y-3">
              {candidate.resumes.map((r) => (
                <div key={r.id} className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <div>
                    <p className="font-medium text-sm">{r.file_name}</p>
                    <p className="text-xs text-gray-500">
                      Uploaded {new Date(r.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setPreviewText(previewText === r.id ? null : r.id)}
                      className="btn-secondary text-xs py-1.5 px-3"
                    >
                      Preview Text
                    </button>
                    <button
                      onClick={() => handleDownload(r)}
                      className="btn-primary text-xs py-1.5 px-3 flex items-center gap-1"
                    >
                      <Download className="w-3 h-3" /> Download
                    </button>
                  </div>
                </div>
              ))}
            </div>
            {previewText && (
              <div className="mt-4 p-4 rounded-lg bg-gray-100 dark:bg-gray-800 max-h-64 overflow-y-auto">
                <pre className="text-xs whitespace-pre-wrap font-mono">
                  {candidate.resumes.find((r) => r.id === previewText)?.parsed_text?.slice(0, 2000) || 'No text available'}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}
