import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import LoadingSpinner from '../components/LoadingSpinner'
import { getCandidates, deleteCandidate } from '../api/client'
import { Search, Trash2, Eye, ChevronLeft, ChevronRight } from 'lucide-react'
import { getErrorMessage } from '../utils/errors'

export default function CandidatesList() {
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const pageSize = 10

  const fetchCandidates = () => {
    setLoading(true)
    getCandidates({ search, page, page_size: pageSize })
      .then(({ data }) => setCandidates(data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchCandidates() }, [search, page])

  const handleDelete = async (id, name) => {
    if (!confirm(`Delete candidate "${name || 'Unknown'}" and their account? This cannot be undone.`)) return
    try {
      await deleteCandidate(id)
      fetchCandidates()
    } catch (err) {
      alert(getErrorMessage(err, 'Delete failed'))
    }
  }

  return (
    <Layout>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold">All Candidates</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Browse and manage candidate profiles</p>
        </div>

        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            className="input-field pl-10"
            placeholder="Search by name, skills, education..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
          />
        </div>

        {loading ? (
          <LoadingSpinner />
        ) : (
          <div className="card overflow-hidden p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 dark:bg-gray-800/50">
                    <th className="text-left py-3 px-4 font-medium">Name</th>
                    <th className="text-left py-3 px-4 font-medium">Email</th>
                    <th className="text-left py-3 px-4 font-medium">Skills</th>
                    <th className="text-left py-3 px-4 font-medium">Resumes</th>
                    <th className="text-left py-3 px-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {candidates.length === 0 ? (
                    <tr><td colSpan={5} className="text-center py-8 text-gray-500">No candidates found</td></tr>
                  ) : (
                    candidates.map((c) => (
                      <tr key={c.id} className="border-t border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/30">
                        <td className="py-3 px-4 font-medium">{c.name || 'Unknown'}</td>
                        <td className="py-3 px-4 text-gray-500">{c.email}</td>
                        <td className="py-3 px-4 text-gray-500 max-w-xs truncate">{c.skills || '—'}</td>
                        <td className="py-3 px-4">{c.resume_count}</td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <Link to={`/candidate/${c.id}`} className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-primary-600">
                              <Eye className="w-4 h-4" />
                            </Link>
                            <button
                              onClick={() => handleDelete(c.id, c.name)}
                              className="p-1.5 rounded hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            <div className="flex items-center justify-between p-4 border-t border-gray-200 dark:border-gray-800">
              <button disabled={page <= 1} onClick={() => setPage(page - 1)} className="btn-secondary flex items-center gap-1 disabled:opacity-50">
                <ChevronLeft className="w-4 h-4" /> Previous
              </button>
              <span className="text-sm text-gray-500">Page {page}</span>
              <button disabled={candidates.length < pageSize} onClick={() => setPage(page + 1)} className="btn-secondary flex items-center gap-1 disabled:opacity-50">
                Next <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}
