import { useState } from 'react';
import { useAuth } from '../lib/auth';
import { mockCourses, mockStats } from '../lib/api';
import {
  BookOpenIcon,
  ChartBarIcon,
  ClockIcon,
  AcademicCapIcon,
  PlayIcon,
  ChevronRightIcon,
  UserIcon,
  CogIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline';
import {
  BookOpenIcon as BookOpenSolidIcon,
  ClockIcon as ClockSolidIcon,
  FireIcon as FireSolidIcon,
  TrophyIcon as TrophySolidIcon,
  UserIcon as UserSolidIcon,
} from '@heroicons/react/24/solid';

type TabType = 'overview' | 'courses' | 'progress' | 'profile';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <AcademicCapIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <h1 className="text-2xl font-bold text-gray-900">X-University</h1>
                <p className="text-sm text-gray-500">Learning Dashboard</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
                <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
              </div>
              <button
                onClick={handleLogout}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
              >
                <ArrowRightOnRectangleIcon className="h-4 w-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">
            {getGreeting()}, {user?.full_name?.split(' ')[0]}!
          </h2>
          <p className="mt-2 text-gray-600">
            Ready to continue your learning journey? Here's what's happening today.
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { id: 'overview', name: 'Overview', icon: ChartBarIcon },
              { id: 'courses', name: 'My Courses', icon: BookOpenIcon },
              { id: 'progress', name: 'Progress', icon: ClockIcon },
              { id: 'profile', name: 'Profile', icon: UserIcon },
            ].map((tab) => {
              const isActive = activeTab === tab.id;
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as TabType)}
                  className={`${
                    isActive
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center transition-colors`}
                >
                  <Icon className="h-5 w-5 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <BookOpenSolidIcon className="h-6 w-6 text-blue-600" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Active Courses
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {mockStats.activeCourses}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <ClockSolidIcon className="h-6 w-6 text-green-600" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Hours Learned
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {mockStats.totalHoursLearned}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <FireSolidIcon className="h-6 w-6 text-orange-600" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Current Streak
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {mockStats.currentStreak} days
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <TrophySolidIcon className="h-6 w-6 text-yellow-600" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Certificates
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {mockStats.certificates}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Continue Learning Section */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Continue Learning</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {mockCourses.slice(0, 2).map((course) => (
                    <div
                      key={course.id}
                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="text-sm font-medium text-gray-900 mb-1">
                            {course.title}
                          </h4>
                          <p className="text-xs text-gray-500 mb-2">
                            Next: {course.nextLesson}
                          </p>
                          <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${course.progress}%` }}
                            ></div>
                          </div>
                          <div className="flex items-center justify-between text-xs text-gray-500">
                            <span>{course.progress}% complete</span>
                            <span>
                              {course.completedLessons}/{course.totalLessons} lessons
                            </span>
                          </div>
                        </div>
                        <button className="ml-4 p-2 text-blue-600 hover:text-blue-800">
                          <PlayIcon className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Weekly Goal */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Weekly Goal</h3>
              </div>
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-medium text-gray-900">
                    {mockStats.weeklyCompletedHours} / {mockStats.weeklyGoalHours} hours completed
                  </span>
                  <span className="text-sm text-gray-500">
                    {Math.round((mockStats.weeklyCompletedHours / mockStats.weeklyGoalHours) * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-green-600 h-3 rounded-full"
                    style={{
                      width: `${Math.min((mockStats.weeklyCompletedHours / mockStats.weeklyGoalHours) * 100, 100)}%`,
                    }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'courses' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {mockCourses.map((course) => (
              <div
                key={course.id}
                className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow"
              >
                <div className="h-48 bg-gray-200 relative">
                  <img
                    src={course.image}
                    alt={course.title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
                  <div className="absolute bottom-4 left-4 right-4">
                    <span className="inline-block px-2 py-1 text-xs font-medium bg-blue-600 text-white rounded">
                      {course.category}
                    </span>
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    {course.title}
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">{course.description}</p>
                  
                  <div className="flex items-center text-xs text-gray-500 mb-4">
                    <span>{course.instructor}</span>
                    <span className="mx-2">•</span>
                    <span>{course.difficulty}</span>
                    <span className="mx-2">•</span>
                    <span>{course.estimatedTime}</span>
                  </div>

                  <div className="mb-4">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600">Progress</span>
                      <span className="font-medium">{course.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${course.progress}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">
                      {course.completedLessons}/{course.totalLessons} lessons
                    </span>
                    <button className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                      Continue
                      <ChevronRightIcon className="ml-1 h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'progress' && (
          <div className="space-y-6">
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-6">Learning Statistics</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600 mb-2">
                    {mockStats.averageProgress}%
                  </div>
                  <div className="text-sm text-gray-500">Average Progress</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600 mb-2">
                    {mockStats.completedCourses}
                  </div>
                  <div className="text-sm text-gray-500">Completed Courses</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-orange-600 mb-2">
                    {mockStats.totalHoursLearned}h
                  </div>
                  <div className="text-sm text-gray-500">Total Hours</div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="text-md font-medium text-gray-900">Course Progress</h4>
                {mockCourses.map((course) => (
                  <div key={course.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="text-sm font-medium text-gray-900">{course.title}</h5>
                      <span className="text-sm font-medium text-gray-900">{course.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${course.progress}%` }}
                      ></div>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>
                        {course.completedLessons} of {course.totalLessons} lessons completed
                      </span>
                      <span>Next: {course.nextLesson}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'profile' && (
          <div className="max-w-3xl mx-auto">
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-6 py-8 sm:px-8">
                <div className="flex items-center">
                  <div className="h-20 w-20 rounded-full bg-gray-300 flex items-center justify-center">
                    <UserSolidIcon className="h-12 w-12 text-gray-600" />
                  </div>
                  <div className="ml-6">
                    <h2 className="text-2xl font-bold text-gray-900">{user?.full_name}</h2>
                    <p className="text-sm text-gray-500 capitalize">{user?.role}</p>
                    <p className="text-sm text-gray-500">{user?.email}</p>
                  </div>
                </div>
              </div>
              
              <div className="border-t border-gray-200 px-6 py-6 sm:px-8">
                <dl className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Member since</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {user?.created_at ? formatDate(user.created_at) : 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Last login</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {user?.last_login ? formatDate(user.last_login) : 'First time login'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Account status</dt>
                    <dd className="mt-1">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        user?.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {user?.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Email verified</dt>
                    <dd className="mt-1">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        user?.email_verified ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {user?.email_verified ? 'Verified' : 'Pending'}
                      </span>
                    </dd>
                  </div>
                </dl>
              </div>

              <div className="border-t border-gray-200 px-6 py-4 sm:px-8">
                <button className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                  <CogIcon className="h-4 w-4 mr-2" />
                  Edit Profile
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
