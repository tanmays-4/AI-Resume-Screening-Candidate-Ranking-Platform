import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 responses globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      localStorage.removeItem('userId')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// --- Auth ---
export const register = (data) => api.post('/register', data)
export const login = (data) => api.post('/login', data)

// --- Candidates ---
export const uploadResume = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload-resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const getCandidates = (params) => api.get('/candidates', { params })
export const getCandidate = (id) => api.get(`/candidate/${id}`)
export const getMyProfile = () => api.get('/candidate/me/profile')
export const deleteCandidate = (id) => api.delete(`/candidate/${id}`)
export const downloadResume = (id) =>
  api.get(`/resume/${id}/preview`, { responseType: 'blob' })

// --- Jobs ---
export const createJob = (data) => api.post('/create-job', data)
export const getJobs = () => api.get('/jobs')
export const deleteJob = (id) => api.delete(`/jobs/${id}`)

// --- Ranking ---
export const rankCandidates = (data) => api.post('/rank', data)
export const exportRankedCSV = (data) =>
  api.post('/rank/export', data, { responseType: 'blob' })

// --- Analytics ---
export const getAnalytics = () => api.get('/analytics')

export default api
