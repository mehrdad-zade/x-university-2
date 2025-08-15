# X University Frontend

## Requirements
- Node.js >= 20.0 (tested with 23.6.1)
- npm (latest version recommended)

## Technology Stack
- **React 18** - Modern React with hooks and concurrent features
- **TypeScript** - Full type safety across the application
- **Vite** - Fast build tool with HMR
- **React Router DOM** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API communication
- **Zod** - TypeScript-first schema validation
- **Zustand** - Lightweight state management

## Project Structure
```
frontend/
└── src/
    ├── components/   # Reusable UI components
    │   ├── ui/           # Basic UI components (buttons, inputs, etc.)
    │   └── layout/       # Layout components (headers, footers, etc.)
    ├── lib/          # Utilities and shared code
    │   ├── api.ts        # API client configuration
    │   ├── auth.ts       # Authentication utilities
    │   └── utils.ts      # General utility functions
    ├── pages/        # Page components
    │   ├── auth/         # Authentication pages
    │   │   ├── LoginPage.tsx     # User login
    │   │   └── RegisterPage.tsx  # User registration
    │   ├── legal/        # Legal pages
    │   │   ├── TermsPage.tsx     # Terms of Service
    │   │   └── PrivacyPage.tsx   # Privacy Policy
    │   └── DashboardPage.tsx     # User dashboard
    ├── routes/       # Route definitions
    │   └── AppRoutes.tsx # Main routing configuration
    └── styles/       # Global styles and Tailwind config
```

## Key Features

### 🔐 Enhanced Registration System
The registration system includes modern UX patterns and comprehensive validation:

#### Real-time Form Validation
- **Email validation**: Format checking and uniqueness verification
- **Password strength indicator**: Visual feedback with color-coded strength levels
- **Form state management**: Real-time validation with immediate feedback
- **Error handling**: Clear, user-friendly error messages

#### Password Security Features
- **Strength requirements**: 8+ characters, uppercase, lowercase, numbers, symbols
- **Visual strength indicator**: Red (weak) → Yellow (medium) → Green (strong)
- **Real-time validation**: Immediate feedback as user types
- **Common password detection**: Prevents weak or common passwords

#### User Experience Enhancements
- **Role selection**: Visual role picker for student/instructor/admin
- **Terms acceptance**: Integrated terms of service and privacy policy acceptance
- **Auto-login**: Automatic login after successful registration
- **Responsive design**: Mobile-first design with Tailwind CSS
- **Loading states**: Proper loading indicators and disabled states

#### Modern UI Design
- **Tailwind CSS styling**: Utility-first approach with custom components
- **Consistent design language**: Matches login page styling
- **Accessibility**: ARIA labels and keyboard navigation support
- **Form layout**: Clean, intuitive form structure

## Development
1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Format code:
```bash
npm run format
```

4. Type checking:
```bash
npm run type-check
```

5. Build for production:
```bash
npm run build
```

## Architecture Notes
- Full TypeScript support
- Component-based architecture
- Responsive design with Tailwind CSS
- Strict ESLint configuration
- Prettier for consistent formatting
