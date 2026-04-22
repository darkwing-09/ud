import React from 'react'

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg border border-gray-100 p-8 text-center space-y-6">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-indigo-100 mb-4">
          <span className="text-3xl">🏫</span>
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">
          EduCore
        </h1>
        <p className="text-gray-500">
          The all-in-one school automation platform.
        </p>
        <div className="pt-4 space-y-4">
          <button className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors">
            Proceed to Login
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
