import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import ProtectedRoute from './components/ProtectedRoute'
import LoadingSpinner from './components/LoadingSpinner'

import Login from './pages/Login'
import Register from './pages/Register'
import CandidateDashboard from './pages/CandidateDashboard'
import RecruiterDashboard from './pages/RecruiterDashboard'
import UploadResume from './pages/UploadResume'
import CreateJob from './pages/CreateJob'
import JobsList from './pages/JobsList'
import RankCandidates from './pages/RankCandidates'
import CandidateProfile from './pages/CandidateProfile'
import CandidatesList from './pages/CandidatesList'
import Analytics from './pages/Analytics'

function RootRedirect() {
  const { user, loading } = useAuth()
  if (loading) return <LoadingSpinner fullScreen />
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to={user.role === 'recruiter' ? '/recruiter' : '/candidate'} replace />
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<RootRedirect />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Candidate routes */}
            <Route path="/candidate" element={
              <ProtectedRoute allowedRole="candidate"><CandidateDashboard /></ProtectedRoute>
            } />
            <Route path="/upload" element={
              <ProtectedRoute allowedRole="candidate"><UploadResume /></ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute allowedRole="candidate"><CandidateProfile /></ProtectedRoute>
            } />

            {/* Recruiter routes */}
            <Route path="/recruiter" element={
              <ProtectedRoute allowedRole="recruiter"><RecruiterDashboard /></ProtectedRoute>
            } />
            <Route path="/create-job" element={
              <ProtectedRoute allowedRole="recruiter"><CreateJob /></ProtectedRoute>
            } />
            <Route path="/jobs" element={
              <ProtectedRoute allowedRole="recruiter"><JobsList /></ProtectedRoute>
            } />
            <Route path="/rank" element={
              <ProtectedRoute allowedRole="recruiter"><RankCandidates /></ProtectedRoute>
            } />
            <Route path="/candidates" element={
              <ProtectedRoute allowedRole="recruiter"><CandidatesList /></ProtectedRoute>
            } />
            <Route path="/analytics" element={
              <ProtectedRoute allowedRole="recruiter"><Analytics /></ProtectedRoute>
            } />
            <Route path="/candidate/:id" element={
              <ProtectedRoute><CandidateProfile /></ProtectedRoute>
            } />

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}
