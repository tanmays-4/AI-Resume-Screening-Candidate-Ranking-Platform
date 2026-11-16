import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import LoadingSpinner from './LoadingSpinner'

export default function ProtectedRoute({ children, allowedRole }) {
  const { user, loading } = useAuth()

  if (loading) return <LoadingSpinner fullScreen />

  if (!user) return <Navigate to="/login" replace />

  if (allowedRole && user.role !== allowedRole) {
    const redirect = user.role === 'recruiter' ? '/recruiter' : '/candidate'
    return <Navigate to={redirect} replace />
  }

  return children
}
