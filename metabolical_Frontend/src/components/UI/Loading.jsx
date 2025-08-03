import React from 'react'

function Loading() {
  return (
    <div className="flex justify-center items-center py-12  w-full">
    <div className="animate-spin rounded-full h-20 w-20 border-b-2 border-violet-700 dark:border-violet-400"></div>
  </div>
  )
}

export default Loading