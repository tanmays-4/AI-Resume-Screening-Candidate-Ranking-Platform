/**
 * Turn an axios error into a human-readable message.
 * FastAPI returns `detail` as a string for HTTPException, but as an array of
 * objects for 422 validation errors — rendering that array directly crashes React.
 */
export function getErrorMessage(err, fallback = 'Something went wrong') {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((d) => {
        const field = Array.isArray(d.loc) ? d.loc.filter((l) => l !== 'body').join('.') : ''
        return field ? `${field}: ${d.msg}` : d.msg
      })
      .join('; ')
  }
  if (err?.code === 'ERR_NETWORK') return 'Cannot reach the server. Is the backend running?'
  return fallback
}
