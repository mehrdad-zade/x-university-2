/**
 * Frontend constants loaded from centralized development configuration.
 * This file provides TypeScript-friendly access to the common dev.config.json.
 */

// Import the dev config - in a real app you'd load this via fetch or build process
// For now, we'll inline the essential parts for type safety
import devConfig from './dev.config.json';

// =============================================================================
// TYPE DEFINITIONS
// =============================================================================
export type UserRole = 'admin' | 'instructor' | 'student';

export interface UserCredentials {
  email: string;
  password: string;
  fullName: string;
  role: UserRole;
}

export type StatusState = 'loading' | 'success' | 'error' | 'warning' | 'info' | 'idle';

// =============================================================================
// URLS & ENDPOINTS
// =============================================================================
export const URLS = {
  FRONTEND: devConfig.urls.frontend,
  BACKEND_BASE: devConfig.urls.backend,
  API_BASE: devConfig.urls.api_base,
  HEALTH_CHECK: devConfig.urls.health_check,
  API_DOCS: devConfig.urls.api_docs,
  
  AUTH: {
    LOGIN: devConfig.endpoints.auth.login,
    REGISTER: devConfig.endpoints.auth.register,
    LOGOUT: devConfig.endpoints.auth.logout,
    REFRESH: devConfig.endpoints.auth.refresh,
    ME: devConfig.endpoints.auth.me,
  },
  
  MONITOR: {
    BASE: devConfig.endpoints.monitor.base,
    DATABASE: devConfig.endpoints.monitor.database,
    LOGS: devConfig.endpoints.monitor.logs,
    DOCKER: devConfig.endpoints.monitor.docker,
  },
} as const;

// =============================================================================
// USER CREDENTIALS (Development Only)
// =============================================================================
export const DEV_CREDENTIALS = {
  DEFAULT_PASSWORD: devConfig.credentials.default_password,
  
  ADMIN: {
    email: devConfig.credentials.users.admin.email,
    password: devConfig.credentials.default_password,
    fullName: devConfig.credentials.users.admin.full_name,
    role: 'admin' as const,
  },
  
  INSTRUCTOR: {
    email: devConfig.credentials.users.instructor.email,
    password: devConfig.credentials.default_password,
    fullName: devConfig.credentials.users.instructor.full_name,
    role: 'instructor' as const,
  },
  
  STUDENT: {
    email: devConfig.credentials.users.student.email,
    password: devConfig.credentials.default_password,
    fullName: devConfig.credentials.users.student.full_name,
    role: 'student' as const,
  },
} as const;

// =============================================================================
// MESSAGES
// =============================================================================
export const MESSAGES = {
  AUTH: {
    LOGIN_SUCCESS: devConfig.messages.auth.login_success,
    LOGIN_FAILED: devConfig.messages.auth.login_failed,
    LOGOUT_SUCCESS: devConfig.messages.auth.logout_success,
  },
  
  STATUS: {
    BACKEND_HEALTHY: devConfig.messages.status.backend_healthy,
    BACKEND_UNHEALTHY: devConfig.messages.status.backend_unhealthy,
    FRONTEND_RUNNING: devConfig.messages.status.frontend_running,
    DATABASE_CONNECTED: devConfig.messages.status.database_connected,
    ALL_SYSTEMS_OPERATIONAL: devConfig.messages.status.all_systems_operational,
  },
  
  ERRORS: {
    NETWORK_ERROR: 'Network error occurred',
    UNAUTHORIZED: 'Unauthorized access',
    SERVER_ERROR: 'Internal server error',
    INVALID_CREDENTIALS: 'Invalid email or password',
    UNEXPECTED_ERROR: 'An unexpected error occurred. Please try again.',
  },
} as const;

// =============================================================================
// UI TEXT
// =============================================================================
export const UI_TEXT = {
  NAVIGATION: {
    HOME: devConfig.ui_text.navigation.home,
    DASHBOARD: devConfig.ui_text.navigation.dashboard,
    COURSES: devConfig.ui_text.navigation.courses,
    MONITOR: devConfig.ui_text.navigation.monitor,
    LOGIN: devConfig.ui_text.navigation.login,
    LOGOUT: devConfig.ui_text.navigation.logout,
  },
  
  BUTTONS: {
    SAVE: devConfig.ui_text.buttons.save,
    CANCEL: devConfig.ui_text.buttons.cancel,
    SUBMIT: devConfig.ui_text.buttons.submit,
    DELETE: devConfig.ui_text.buttons.delete,
    EDIT: devConfig.ui_text.buttons.edit,
    DEMO_ADMIN: devConfig.ui_text.buttons.demo_admin,
    DEMO_INSTRUCTOR: devConfig.ui_text.buttons.demo_instructor,
    DEMO_STUDENT: devConfig.ui_text.buttons.demo_student,
  },
  
  FORMS: {
    EMAIL: devConfig.ui_text.forms.email,
    PASSWORD: devConfig.ui_text.forms.password,
    FULL_NAME: devConfig.ui_text.forms.full_name,
    CONFIRM_PASSWORD: devConfig.ui_text.forms.confirm_password,
  },
  
  LOGIN: {
    SIGN_IN_TITLE: devConfig.ui_text.login.sign_in_title,
    ACCESS_DASHBOARD: devConfig.ui_text.login.access_dashboard,
    DEMO_ACCOUNTS: devConfig.ui_text.login.demo_accounts,
    SIGNING_IN: devConfig.ui_text.login.signing_in,
    SIGN_IN: devConfig.ui_text.login.sign_in,
    DEMO_NOTE: devConfig.ui_text.login.demo_note,
  },
  
  MONITOR: {
    TITLE: devConfig.ui_text.monitor.title,
    LOGS_TITLE: devConfig.ui_text.monitor.logs_title,
    DB_PERFORMANCE_TITLE: devConfig.ui_text.monitor.db_performance_title,
    DOCKER_CONTAINERS_TITLE: devConfig.ui_text.monitor.docker_containers_title,
    SHOW_LOGS: '⬇️ Show Logs',
    HIDE_LOGS: '⬆️ Hide Logs',
    SHOW_PERFORMANCE: '⬇️ Show Performance',
    HIDE_PERFORMANCE: '⬆️ Hide Performance',
    SHOW_DOCKER: '⬇️ Show Docker Containers',
    HIDE_DOCKER: '⬆️ Hide Docker Containers',
  },
  
  DASHBOARD: {
    WELCOME: 'Welcome to X-University',
    YOUR_COURSES: 'Your Courses',
    RECENT_ACTIVITY: 'Recent Activity',
    PROGRESS: 'Your Progress',
  },
} as const;

// =============================================================================
// STATUS & CONFIGURATION
// =============================================================================
export const STATUS = {
  HTTP: {
    OK: 200,
    CREATED: 201,
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    UNPROCESSABLE_ENTITY: 422,
    INTERNAL_SERVER_ERROR: 500,
  },
  
  STATES: {
    LOADING: 'loading',
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info',
    IDLE: 'idle',
  },
} as const;

export const CONFIG = {
  // Timeouts from dev config
  TIMEOUTS: {
    API_TIMEOUT: 10000,
    AUTH_RETRY_DELAY: 1000,
    HEALTH_CHECK_INTERVAL: devConfig.timeouts.health_check_interval * 1000, // Convert to ms
    CONNECTION_RETRY: devConfig.timeouts.connection_retry,
  },
  
  // Local Storage Keys
  STORAGE_KEYS: {
    AUTH_TOKEN: 'xu2_auth_token',
    REFRESH_TOKEN: 'xu2_refresh_token',
    USER_DATA: 'xu2_user_data',
    THEME_PREFERENCE: 'xu2_theme',
    MONITOR_PREFERENCES: 'xu2_monitor_prefs',
  },
  
  // CSS Classes for Status Colors
  STATUS_COLORS: {
    success: 'text-green-600 bg-green-100',
    error: 'text-red-600 bg-red-100',
    warning: 'text-yellow-600 bg-yellow-100',
    info: 'text-blue-600 bg-blue-100',
    loading: 'text-gray-600 bg-gray-100',
    idle: 'text-gray-500 bg-gray-50',
  },
} as const;

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Get demo credentials for a specific role
 */
export function getDemoCredentials(role: UserRole): UserCredentials | null {
  switch (role) {
    case 'admin':
      return DEV_CREDENTIALS.ADMIN;
    case 'instructor':
      return DEV_CREDENTIALS.INSTRUCTOR;
    case 'student':
      return DEV_CREDENTIALS.STUDENT;
    default:
      return null;
  }
}

/**
 * Build a full API URL from an endpoint
 */
export function buildApiUrl(endpoint: string): string {
  if (endpoint.startsWith('http')) {
    return endpoint;
  }
  if (endpoint.startsWith('/api/v1/')) {
    return `${URLS.BACKEND_BASE}${endpoint}`;
  }
  return `${URLS.API_BASE}${endpoint}`;
}

/**
 * Build a full backend URL from an endpoint
 */
export function buildBackendUrl(endpoint: string): string {
  if (endpoint.startsWith('http')) {
    return endpoint;
  }
  return `${URLS.BACKEND_BASE}${endpoint}`;
}

/**
 * Get status color class for a given state
 */
export function getStatusColor(status: StatusState): string {
  return CONFIG.STATUS_COLORS[status] || CONFIG.STATUS_COLORS.info;
}

/**
 * Get user credentials by role (alias for getDemoCredentials)
 */
export function getUserByRole(role: UserRole): UserCredentials | null {
  return getDemoCredentials(role);
}

/**
 * Check if a user has admin privileges
 */
export function isAdminRole(role: string): boolean {
  return role === 'admin';
}

/**
 * Check if a user has instructor privileges
 */
export function isInstructorRole(role: string): boolean {
  return role === 'instructor' || role === 'admin';
}
