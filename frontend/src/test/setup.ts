import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock fetch globally for tests
Object.defineProperty(globalThis, 'fetch', {
  writable: true,
  value: vi.fn()
})

// Mock localStorage
const mockLocalStorage = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key]
    }),
    clear: vi.fn(() => {
      store = {}
    })
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
})

// Mock ResizeObserver
Object.defineProperty(globalThis, 'ResizeObserver', {
  writable: true,
  value: vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn()
  }))
})

// Suppress specific React warnings in tests
const originalConsoleError = console.error
console.error = (...args) => {
  // Suppress React Router Future Flag warnings and act() warnings in test environment
  if (
    typeof args[0] === 'string' && 
    (args[0].includes('React Router Future Flag Warning') ||
     args[0].includes('Warning: An update to') ||
     args[0].includes('wrapped in act(...)')
    )
  ) {
    return
  }
  originalConsoleError.apply(console, args)
}
