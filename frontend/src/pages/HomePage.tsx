import { Link } from 'react-router-dom'

export default function HomePage() {
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
          <Link
            to="/courses"
            className="rounded-md bg-primary-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
          >
            Browse Courses
          </Link>
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
            <h3 className="text-lg font-semibold text-gray-900">Expert-Led Courses</h3>
            <p className="mt-2 text-gray-600">
              Learn from industry professionals with years of experience in their fields.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900">AI-Powered Learning</h3>
            <p className="mt-2 text-gray-600">
              Get personalized learning paths and AI-generated content tailored to your needs.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900">Progress Tracking</h3>
            <p className="mt-2 text-gray-600">
              Monitor your learning journey with detailed analytics and progress reports.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
