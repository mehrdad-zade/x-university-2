# X University Frontend

## Requirements
- Node.js >= 20.0 (tested with 23.6.1)
- npm (latest version recommended)

## Technology Stack
- React 18
- TypeScript
- Vite
- React Router DOM
- Tailwind CSS
- Axios
- Zod
- Zustand (State Management)

## Project Structure
```
frontend/
└── src/
    ├── components/   # Reusable UI components
    ├── lib/          # Utilities and shared code
    ├── pages/        # Page components
    ├── routes/       # Route definitions
    └── styles/       # Global styles and Tailwind config
```

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
