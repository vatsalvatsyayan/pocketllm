# pocketLLM Portal - Frontend

A professional authentication system built with React, TypeScript, and Tailwind CSS for the pocketLLM portal. This frontend application provides a complete login/signup flow with mocked authentication, designed for easy integration with a real backend API.

## Features

- **Professional Authentication UI**: Modern login and signup pages with the pocketLLM aesthetic
- **Type-Safe Development**: Full TypeScript support with strict type checking
- **Mock Authentication**: Fully functional mock auth service for development and testing
- **Easy API Integration**: Interface-based architecture for seamless real API swap
- **Responsive Design**: Mobile-first design that works on all devices
- **Accessible**: ARIA labels, keyboard navigation, and screen reader support
- **Form Validation**: Real-time validation with user-friendly error messages
- **Protected Routes**: Route guards for authenticated-only pages
- **Session Persistence**: Automatic session restoration on page reload
- **Clean Architecture**: SOLID principles, separation of concerns, reusable components

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router 6** - Routing
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Context API** - State management

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Git

### Installation

1. **Navigate to the frontend folder** (if not already there):
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Open your browser**:
   Navigate to `http://localhost:5173`

### Demo Credentials

```
Email: demo@pocketllm.com
Password: demo123
```

Or create a new account using the signup page!

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/             # Base UI components (Button, Input, Card, etc.)
│   │   ├── auth/           # Authentication components (LoginForm, SignupForm, ProtectedRoute)
│   │   └── layout/         # Layout components (AuthLayout, DashboardLayout)
│   ├── pages/              # Page components
│   │   ├── Login.tsx       # Login page
│   │   ├── Signup.tsx      # Signup page
│   │   ├── Dashboard.tsx   # Protected dashboard
│   │   └── NotFound.tsx    # 404 page
│   ├── services/           # Business logic and API layer
│   │   ├── api/           # API client and endpoints
│   │   ├── auth/          # Authentication services (mock and interface)
│   │   └── storage/       # Token and data storage utilities
│   ├── context/           # React context providers
│   │   └── AuthContext.tsx # Global auth state
│   ├── hooks/             # Custom React hooks
│   │   ├── useAuth.ts     # Auth context hook
│   │   ├── useForm.ts     # Form management hook
│   │   └── useLocalStorage.ts # LocalStorage hook
│   ├── types/             # TypeScript type definitions
│   │   ├── auth.types.ts  # Authentication types
│   │   ├── user.types.ts  # User model types
│   │   └── api.types.ts   # API response types
│   ├── utils/             # Utility functions
│   │   ├── constants.ts   # App constants
│   │   ├── validation.ts  # Form validation
│   │   ├── errorHandler.ts # Error handling
│   │   └── cn.ts          # Class name utility
│   ├── styles/            # Global styles
│   │   └── index.css      # Tailwind imports and custom styles
│   ├── App.tsx            # Main app component with routing
│   ├── main.tsx           # Application entry point
│   └── vite-env.d.ts      # Vite type definitions
├── public/                # Static assets
├── index.html             # HTML template
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── vite.config.ts         # Vite configuration
├── .env.example           # Environment variables example
├── .env.local             # Local environment variables
└── README.md              # This file
```

## Architecture

### Authentication Flow

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  LoginForm/     │ ◄─── Validates input
│  SignupForm     │      Handles UI state
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AuthContext    │ ◄─── Global auth state
│  (useAuth)      │      Login/logout functions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AuthService    │ ◄─── Interface-based design
│  (mock/real)    │      Easy to swap implementations
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Token Storage  │ ◄─── Persistent session
│  (localStorage)  │      Token management
└─────────────────┘
```

### Component Hierarchy

```
App (BrowserRouter + AuthProvider)
├── Login Page
│   └── AuthLayout
│       └── LoginForm
│           ├── Input components
│           ├── Button component
│           └── Alert component
├── Signup Page
│   └── AuthLayout
│       └── SignupForm
│           ├── Input components
│           ├── Button component
│           └── Alert component
└── Dashboard (Protected)
    └── DashboardLayout
        └── Dashboard content
```

## How to Swap Mock Auth with Real API

The authentication system is designed with the **Dependency Inversion Principle** to make swapping implementations trivial.

### Current Setup (Mock)

```typescript
// src/services/auth/index.ts
import { mockAuthService } from './mockAuthService';

export const authService = mockAuthService;
```

### Steps to Integrate Real API

1. **Create the real API service**:

   Create `src/services/auth/apiAuthService.ts`:

   ```typescript
   import { IAuthService } from './authService.interface';
   import { apiClient } from '../api/apiClient';
   import { AUTH_ENDPOINTS } from '../api/endpoints';

   export class ApiAuthService implements IAuthService {
     async login(credentials: LoginCredentials): Promise<AuthResponse> {
       const response = await apiClient.post(
         AUTH_ENDPOINTS.LOGIN,
         credentials
       );
       return response;
     }

     async signup(credentials: SignupCredentials): Promise<AuthResponse> {
       const response = await apiClient.post(
         AUTH_ENDPOINTS.SIGNUP,
         credentials
       );
       return response;
     }

     async logout(): Promise<void> {
       await apiClient.post(AUTH_ENDPOINTS.LOGOUT);
     }

     async validateToken(token: string): Promise<TokenValidationResponse> {
       const response = await apiClient.post(
         AUTH_ENDPOINTS.VALIDATE,
         { token }
       );
       return response;
     }

     async refreshToken(refreshToken: string): Promise<AuthResponse> {
       const response = await apiClient.post(
         AUTH_ENDPOINTS.REFRESH,
         { refreshToken }
       );
       return response;
     }
   }

   export const apiAuthService = new ApiAuthService();
   ```

2. **Update the export** in `src/services/auth/index.ts`:

   ```typescript
   // Comment out mock service
   // import { mockAuthService } from './mockAuthService';

   // Import real API service
   import { apiAuthService } from './apiAuthService';

   // Change export
   export const authService = apiAuthService;
   ```

3. **Update environment variables** in `.env.local`:

   ```env
   VITE_API_BASE_URL=https://your-backend-api.com/api
   VITE_MOCK_AUTH=false
   ```

4. **That's it!** No changes needed in components, context, or pages.

### API Contracts

The backend should match these TypeScript interfaces:

**Login Request:**
```typescript
{
  email: string;
  password: string;
  rememberMe?: boolean;
}
```

**Signup Request:**
```typescript
{
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}
```

**Auth Response:**
```typescript
{
  token: string;
  user: {
    id: string;
    email: string;
    name: string;
    createdAt: string;
    role?: 'user' | 'admin';
  };
  expiresIn?: number; // seconds
}
```

**Error Response:**
```typescript
{
  code: string;
  message: string;
  statusCode: number;
  details?: any;
}
```

## Environment Variables

Create a `.env.local` file (already included) with these variables:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:3000/api
VITE_AUTH_TOKEN_KEY=pocketllm_auth_token

# Mock Authentication Toggle
VITE_MOCK_AUTH=true

# Application Settings
VITE_APP_NAME=pocketLLM Portal
VITE_APP_VERSION=1.0.0
```

## Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## Design System

### Colors

- **Primary**: Indigo/Blue (`#4F46E5`, `#3B82F6`)
- **Accent**: Cyan (`#06B6D4`)
- **Background**: Dark gradient (`#0F172A` → `#1E293B`)
- **Surface**: Dark with subtle gradient (`#1E293B`)
- **Text**: White/Gray (`#F8FAFC`, `#CBD5E1`)

### Components

All UI components are located in `src/components/ui/`:

- **Button**: Multiple variants (primary, secondary, outline, ghost, danger)
- **Input**: With labels, errors, helper text, and icons
- **Card**: Container with glassmorphism effect
- **Alert**: Info, success, warning, error variants
- **LoadingSpinner**: With sizes and full-screen mode

## Best Practices

### Code Organization

1. **Separation of Concerns**: Components, services, types, and utilities are clearly separated
2. **Single Responsibility**: Each file has one clear purpose
3. **DRY Principle**: Reusable components and utilities
4. **Type Safety**: Strict TypeScript with no `any` types
5. **Clean Code**: Comprehensive comments and JSDoc

### Component Guidelines

1. Use functional components with hooks
2. Prefer named exports for components
3. Always define TypeScript interfaces for props
4. Extract complex logic into custom hooks
5. Keep components under 200 lines

### State Management

1. Use `useState` for local component state
2. Use Context API for global state (auth)
3. Consider adding Redux/Zustand for complex state needs

## Security Considerations

### Current Implementation (Development)

- Tokens stored in localStorage
- Client-side validation only
- Mock authentication

### Production Recommendations

1. **Use httpOnly cookies** for token storage (prevents XSS)
2. **Implement CSRF protection** on backend
3. **Use HTTPS** for all requests
4. **Add rate limiting** for login attempts
5. **Implement proper password hashing** on backend
6. **Add refresh token rotation**
7. **Set up Content Security Policy (CSP)**

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

When adding new features:

1. Follow the existing folder structure
2. Add TypeScript types for all new interfaces
3. Create reusable components when possible
4. Add comprehensive comments
5. Update this README if needed

## Troubleshooting

### Port already in use

```bash
# Kill process on port 5173
npx kill-port 5173

# Or change port in vite.config.ts
```

### TypeScript errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Styling not working

```bash
# Rebuild Tailwind
npm run dev
```

## Future Enhancements

- [ ] Password reset flow
- [ ] Email verification
- [ ] OAuth providers (Google, GitHub)
- [ ] Two-factor authentication
- [ ] Remember me functionality
- [ ] Dark/light mode toggle
- [ ] Toast notifications
- [ ] Unit and integration tests
- [ ] Storybook for component library

## Team Collaboration

### For Backend Developers

- API contracts: `src/types/auth.types.ts`
- Expected endpoints: `src/services/api/endpoints.ts`
- JWT token expected in response
- CORS configuration needed

### For Designers

- Color palette: `tailwind.config.js`
- Component library: `src/components/ui/`
- Design tokens centralized in Tailwind config

### For DevOps

- Environment variables: `.env.example`
- Build output: `dist/`
- Static file hosting compatible
- Docker containerization possible

## License

MIT

## Support

For issues or questions:
- Check the `login_signup_plan.md` for implementation details
- Review code comments for architecture explanations
- Consult TypeScript types for API contracts

---

**Built with ❤️ for pocketLLM Portal**
