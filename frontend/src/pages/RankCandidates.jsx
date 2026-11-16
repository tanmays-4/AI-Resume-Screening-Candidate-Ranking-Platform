import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import Layout from '../components/Layout'
import LoadingSpinner from '../components/LoadingSpinner'
import ScoreBadge from '../components/ScoreBadge'
import { getJobs, rankCandidates, exportRankedCSV } from '../api/client'
import { getErrorMessage } from '../utils/errors'
import { Download, Search, ChevronLeft, ChevronRight, Briefcase, RotateCcw } from 'lucide-react'

const DEFAULT_FILTERS = {
  skills_filter: '',
  experience_filter: '',
  education_filter: '',
  min_match_score: '',
  min_ats_score: '',
  sort_by: 'match_score',
  sort_order: 'desc',
  page_size: 10,
}

export default function RankCandidates() {
  const [searchParams] = useSearchParams()
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [initialLoading, setInitialLoading] = useState(true)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState(DEFAULT_FILTERS)

  useEffect(() => {
    getJobs()
      .then(({ data }) => {
        setJobs(data)
        const requested = searchParams.get('job')
        if (requested && data.some((j) => String(j.id) === requested)) {
          setSelectedJob(requested)
        } else if (data.length > 0) {
          setSelectedJob(String(data[0].id))
        }
      })
      .catch((err) => setError(getErrorMessage(err, 'Failed to load jobs')))
      .finally(() => setInitialLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const buildPayload = (page = 1) => ({
    job_id: parseInt(selectedJob),
    skills_filter: filters.skills_filter.trim() || null,
    experience_filter: filters.experience_filter.trim() || null,
    education_filter: filters.education_filter.trim() || null,
    min_match_score: filters.min_match_score !== '' ? parseFloat(filters.min_match_score) : null,
    min_ats_score: filters.min_ats_score !== '' ? parseFloat(filters.min_ats_score) : null,
    sort_by: filters.sort_by,
    sort_order: filters.sort_order,
    page,
    page_size: filters.page_size,
  })

  const handleRank = async (page = 1) => {
    if (!selectedJob) return
    setLoading(true)
    setError('')
    try {
      const { data } = await rankCandidates(buildPayload(page))
      setResults(data)
    } catch (err) {
      setError(getErrorMessage(err, 'Ranking failed'))
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    if (!selectedJob) return
    setExporting(true)
    try {
      const { data } = await exportRankedCSV(buildPayload(1))
      const job = jobs.find((j) => String(j.id) === selectedJob)
      const safeTitle = (job?.title || 'job').replace(/[^A-Za-z0-9_-]+/g, '_')
      const url = window.URL.createObjectURL(new Blob([data], { type: 'text/csv' }))
      const a = document.createElement('a')
      a.href = url
      a.download = `ranked_candidates_${safeTitle}.csv`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError(getErrorMessage(err, 'Export failed'))
    } finally {
      setExporting(false)
    }
  }

  const setFilter = (key) => (e) => setFilters({ ...filters, [key]: e.target.value })

  if (initialLoading) return <Layout><LoadingSpinner /></Layout>

  const totalPages = results ? Math.max(1, Math.ceil(results.total / results.page_size)) : 1

  return (
    <Layout>
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold">Rank Candidates</h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              AI-powered semantic matching and ATS scoring
            </p>
          </div>
          {results && results.total > 0 && (
            <button onClick={handleExport} disabled={exporting} className="btn-secondary flex items-center gap-2">
              <Download className="w-4 h-4" /> {exporting ? 'Exporting...' : 'Export CSV'}
            </button>
          )}
        </div>

        {error && (
          <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-sm">
            {error}
          </div>
        )}

        {jobs.length === 0 ? (
          <div className="card text-center py-12">
            <Briefcase className="w-12 h-12 mx-auto text-gray-400 mb-3" />
            <p className="font-medium">No jobs yet</p>
            <p className="text-sm text-gray-500 mt-1 mb-4">Create a job description to start ranking candidates.</p>
            <Link to="/create-job" className="btn-primary inline-block">Create Job</Link>
          </div>
        ) : (
          <div className="card space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="lg:col-span-2">
                <label className="block text-sm font-medium mb-1.5">Select Job</label>
                <select
                  className="input-field"
                  value={selectedJob}
                  onChange={(e) => { setSelectedJob(e.target.value); setResults(null) }}
                >
                  {jobs.map((j) => (
                    <option key={j.id} value={j.id}>{j.title}{j.location ? ` — ${j.location}` : ''}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5">Sort By</label>
                <select className="input-field" value={filters.sort_by} onChange={setFilter('sort_by')}>
                  <option value="match_score">Match Score</option>
                  <option value="ats_score">ATS Score</option>
                  <option value="name">Name</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5">Order</label>
                <select className="input-field" value={filters.sort_order} onChange={setFilter('sort_order')}>
                  <option value="desc">Descending</option>
                  <option value="asc">Ascending</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
              <input className="input-field" placeholder="Skill (e.g. Python)" value={filters.skills_filter} onChange={setFilter('skills_filter')} />
              <input className="input-field" placeholder="Experience keyword" value={filters.experience_filter} onChange={setFilter('experience_filter')} />
              <input className="input-field" placeholder="Education keyword" value={filters.education_filter} onChange={setFilter('education_filter')} />
              <input className="input-field" placeholder="Min match score" type="number" min="0" max="100" value={filters.min_match_score} onChange={setFilter('min_match_score')} />
              <input className="input-field" placeholder="Min ATS score" type="number" min="0" max="100" value={filters.min_ats_score} onChange={setFilter('min_ats_score')} />
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => handleRank(1)}
                disabled={!selectedJob || loading}
                className="btn-primary flex items-center gap-2"
              >
                <Search className="w-4 h-4" />
                {loading ? 'Ranking...' : 'Rank Candidates'}
              </button>
              <button
                onClick={() => setFilters(DEFAULT_FILTERS)}
                className="btn-secondary flex items-center gap-2"
                type="button"
              >
                <RotateCcw className="w-4 h-4" /> Reset filters
              </button>
            </div>
          </div>
        )}

        {loading && <LoadingSpinner text="Computing AI scores..." />}

        {results && !loading && (
          <div className="card overflow-hidden p-0">
            <div className="p-4 border-b border-gray-200 dark:border-gray-800">
              <h2 className="font-semibold">
                Results for: {results.job_title}
                <span className="text-gray-500 font-normal ml-2">({results.total} candidates)</span>
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 dark:bg-gray-800/50">
                    <th className="text-left py-3 px-4 font-medium">Rank</th>
                    <th className="text-left py-3 px-4 font-medium">Candidate</th>
                    <th className="text-left py-3 px-4 font-medium">Match Score</th>
                    <th className="text-left py-3 px-4 font-medium">ATS Score</th>
                    <th className="text-left py-3 px-4 font-medium">Missing Skills</th>
                  </tr>
                </thead>
                <tbody>
                  {results.results.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="text-center py-8 text-gray-500">
                        No candidates match. Only candidates who have uploaded a resume are ranked.
                      </td>
                    </tr>
                  ) : (
                    results.results.map((r) => (
                      <tr key={r.candidate_id} className="border-t border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/30">
                        <td className="py-3 px-4">
                          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 font-bold text-sm">
                            #{r.rank}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <Link to={`/candidate/${r.candidate_id}`} className="font-medium text-primary-600 hover:underline">
                            {r.candidate_name}
                          </Link>
                          <p className="text-xs text-gray-500">{r.email}</p>
                        </td>
                        <td className="py-3 px-4"><ScoreBadge score={r.match_score} type="match" /></td>
                        <td className="py-3 px-4"><ScoreBadge score={r.ats_score} type="ats" /></td>
                        <td className="py-3 px-4 max-w-xs">
                          {r.missing_skills ? (
                            <div className="flex flex-wrap gap-1">
                              {r.missing_skills.split(',').map((s) => s.trim()).filter(Boolean).map((s) => (
                                <span key={s} className="px-2 py-0.5 rounded-full text-xs bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400">
                                  {s}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <span className="text-xs text-green-600">None</span>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {results.total > results.page_size && (
              <div className="flex items-center justify-between p-4 border-t border-gray-200 dark:border-gray-800">
                <button
                  disabled={results.page <= 1}
                  onClick={() => handleRank(results.page - 1)}
                  className="btn-secondary flex items-center gap-1 disabled:opacity-50"
                >
                  <ChevronLeft className="w-4 h-4" /> Previous
                </button>
                <span className="text-sm text-gray-500">
                  Page {results.page} of {totalPages}
                </span>
                <button
                  disabled={results.page >= totalPages}
                  onClick={() => handleRank(results.page + 1)}
                  className="btn-secondary flex items-center gap-1 disabled:opacity-50"
                >
                  Next <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}
