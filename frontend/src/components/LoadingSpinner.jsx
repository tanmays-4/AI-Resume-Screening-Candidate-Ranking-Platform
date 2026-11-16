export default function LoadingSpinner({ fullScreen = false, text = 'Loading...' }) {
  const wrapper = fullScreen
    ? 'fixed inset-0 flex items-center justify-center bg-gray-50/80 dark:bg-gray-950/80 z-50'
    : 'flex items-center justify-center py-12'

  return (
    <div className={wrapper}>
      <div className="flex flex-col items-center gap-3">
        <div className="relative">
          <div className="w-12 h-12 rounded-full border-4 border-primary-200 dark:border-primary-900" />
          <div className="absolute top-0 left-0 w-12 h-12 rounded-full border-4 border-transparent border-t-primary-600 animate-spin" />
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400 animate-pulse">{text}</p>
      </div>
    </div>
  )
}
