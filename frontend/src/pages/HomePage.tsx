import { Link } from 'react-router-dom'
import { useAuth } from '../lib/auth'

export default function HomePage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 sm:text-6xl">
          Welcome to X University
        </h1>
        <p className="mt-6 text-lg leading-8 text-gray-600">
          Learn, grow, and excel with our comprehensive online education platform.
          Access courses, track your progress, and connect with expert instructors.
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          {isAuthenticated ? (
            <Link
              to="/dashboard"
              className="rounded-md bg-blue-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
            >
              Go to Dashboard
            </Link>
          ) : (
            <Link
              to="/login"
              className="rounded-md bg-blue-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
            >
              Get Started
            </Link>
          )}
          <Link
            to="/about"
            className="text-sm font-semibold leading-6 text-gray-900"
          >
            Learn more <span aria-hidden="true">→</span>
          </Link>
        </div>
      </div>

      <div className="mt-20">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center mb-4">
              <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <h3 className="ml-3 text-lg font-semibold text-gray-900">Expert-Led Courses</h3>
            </div>
            <p className="text-gray-600">
              Learn from industry professionals with years of experience in their fields.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center mb-4">
              <svg className="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <h3 className="ml-3 text-lg font-semibold text-gray-900">AI-Powered Learning</h3>
            </div>
            <p className="text-gray-600">
              Get personalized learning paths and AI-generated content tailored to your needs.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center mb-4">
              <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <h3 className="ml-3 text-lg font-semibold text-gray-900">Progress Tracking</h3>
            </div>
            <p className="text-gray-600">
              Monitor your learning journey with detailed analytics and progress reports.
            </p>
          </div>
        </div>
      </div>

      {!isAuthenticated && (
        <div className="mt-20 bg-gray-100 rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Ready to Start Learning?</h2>
          <p className="text-gray-600 mb-6">
            Join thousands of students already learning on our platform. Try our demo accounts:
          </p>
          <div className="flex justify-center space-x-4">
            <div className="bg-white p-4 rounded-lg shadow">
              <h4 className="font-semibold text-blue-600">Student Demo</h4>
              <p className="text-sm text-gray-500">student@example.com</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <h4 className="font-semibold text-green-600">Instructor Demo</h4>
              <p className="text-sm text-gray-500">instructor@example.com</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <h4 className="font-semibold text-purple-600">Admin Demo</h4>
              <p className="text-sm text-gray-500">admin@example.com</p>
            </div>
          </div>
          <div className="mt-6">
            <Link
              to="/login"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              Try Demo Now
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
