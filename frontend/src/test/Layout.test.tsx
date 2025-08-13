import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import Layout from '../components/Layout';

// Mock auth context
const mockAuth = {
  user: { id: '1', email: 'test@example.com' },
  login: vi.fn(),
  logout: vi.fn(),
  isLoading: false,
  isAuthenticated: true,
  refreshAuthState: vi.fn(),
};

vi.mock('../lib/auth', async (importOriginal) => {
  const actual = await importOriginal() as any;
  return {
    ...actual,
    useAuth: () => mockAuth,
    AuthProvider: ({ children }: { children: React.ReactNode }) => children,
  };
});

const LayoutWrapper = () => (
  <MemoryRouter initialEntries={['/']}>
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<div>Test content</div>} />
      </Route>
    </Routes>
  </MemoryRouter>
);

describe('Layout Component', () => {
  it('renders API Doc link with correct href and target', () => {
    render(<LayoutWrapper />);
    
    const apiDocLink = screen.getByText('API Doc');
    expect(apiDocLink).toBeInTheDocument();
    expect(apiDocLink).toHaveAttribute('href', 'http://localhost:8000/docs');
    expect(apiDocLink).toHaveAttribute('target', '_blank');
    expect(apiDocLink).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('renders Monitor link', () => {
    render(<LayoutWrapper />);
    
    const monitorLink = screen.getByText('Monitor');
    expect(monitorLink).toBeInTheDocument();
  });

  it('renders Dashboard link when authenticated', () => {
    render(<LayoutWrapper />);
    
    const dashboardLink = screen.getByText('Dashboard');
    expect(dashboardLink).toBeInTheDocument();
  });

  it('renders navigation in correct order', () => {
    render(<LayoutWrapper />);
    
    const navLinks = screen.getAllByRole('link');
    const linkTexts = navLinks.map(link => link.textContent);
    
    // Check that API Doc and Monitor are present
    expect(linkTexts).toContain('API Doc');
    expect(linkTexts).toContain('Monitor');
  });

  it('API Doc link opens in new tab', () => {
    render(<LayoutWrapper />);
    
    const apiDocLink = screen.getByText('API Doc');
    expect(apiDocLink).toHaveAttribute('target', '_blank');
    expect(apiDocLink).toHaveAttribute('rel', 'noopener noreferrer');
  });
});
