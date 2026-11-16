import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import LoadingSpinner from '../components/LoadingSpinner'
import { uploadResume } from '../api/client'
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import { getErrorMessage } from '../utils/errors'

const MAX_SIZE_MB = 10

export default function UploadResume() {
  const navigate = useNavigate()
  const fileRef = useRef(null)
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(null)
  const [dragOver, setDragOver] = useState(false)

  const handleFile = (f) => {
    if (!f) return
    const ext = f.name.split('.').pop().toLowerCase()
    if (!['pdf', 'docx'].includes(ext)) {
      setError('Only PDF and DOCX files are supported')
      return
    }
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`File is too large (max ${MAX_SIZE_MB} MB)`)
      return
    }
    setFile(f)
    setError('')
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setError('')
    try {
      const { data } = await uploadResume(file)
      setSuccess(data)
      setTimeout(() => navigate('/profile'), 2000)
    } catch (err) {
      setError(getErrorMessage(err, 'Upload failed'))
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Layout>
        <LoadingSpinner text="Parsing your resume with AI..." />
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold">Upload Resume</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Upload your PDF or DOCX resume for AI-powered parsing
          </p>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            {error}
          </div>
        )}

        {success && (
          <div className="flex items-center gap-2 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400">
            <CheckCircle className="w-5 h-5 flex-shrink-0" />
            Resume uploaded and parsed successfully! Redirecting...
          </div>
        )}

        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileRef.current?.click()}
          className={`card border-2 border-dashed cursor-pointer transition-all text-center py-12 ${
            dragOver
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/10'
              : 'border-gray-300 dark:border-gray-700 hover:border-primary-400'
          }`}
        >
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.docx"
            className="hidden"
            onChange={(e) => handleFile(e.target.files[0])}
          />
          <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          {file ? (
            <div className="flex items-center justify-center gap-2">
              <FileText className="w-5 h-5 text-primary-600" />
              <span className="font-medium">{file.name}</span>
              <span className="text-sm text-gray-500">({(file.size / 1024).toFixed(1)} KB)</span>
            </div>
          ) : (
            <>
              <p className="font-medium">Drag & drop your resume here</p>
              <p className="text-sm text-gray-500 mt-1">or click to browse (PDF, DOCX — max 10 MB)</p>
            </>
          )}
        </div>

        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="btn-primary w-full py-3 text-lg"
        >
          Upload & Parse Resume
        </button>
      </div>
    </Layout>
  )
}
