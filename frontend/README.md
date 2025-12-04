# Frontend Service

React + TypeScript web application with authentication, chat interface, and session management.

## What This Does

- **Authentication UI**: Login, signup, protected routes
- **Chat Interface**: Streaming chat with TinyLlama
- **Session Management**: Create, view, and manage chat sessions
- **Admin Dashboard**: User management (admin only)
- **Responsive Design**: Mobile-first, Tailwind CSS styling

## Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/         # LoginForm, SignupForm, ProtectedRoute
│   │   ├── chat/         # ChatInterface, MessageList, SessionSidebar
│   │   ├── layout/       # AuthLayout, DashboardLayout
│   │   └── ui/           # Button, Input, Card, Alert, LoadingSpinner
│   ├── pages/            # Login, Signup, ChatPage, Dashboard, AdminDashboard
│   ├── services/
│   │   ├── api/          # API client, endpoints configuration
│   │   ├── auth/         # Auth service (API-backed)
│   │   ├── chat/         # Chat service, streaming handler
│   │   └── storage/      # Token storage utilities
│   ├── context/          # AuthContext (global auth state)
│   ├── hooks/            # useAuth, useChatStream, useForm
│   ├── types/            # TypeScript type definitions
│   └── utils/            # Validation, error handling, constants
├── Dockerfile
├── nginx.conf
└── package.json
```

**Tech Stack**: React 18, TypeScript, Vite, React Router, Tailwind CSS, Lucide Icons

## Running Standalone

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

Runs on http://localhost:5173

**Environment Variables** (`.env.local`):
```env
VITE_API_BASE_URL=http://localhost:9000/api/v1
VITE_AUTH_TOKEN_KEY=pocketllm_auth_token
```

## Demo Credentials

- **Email**: `demo@pocketllm.com`
- **Password**: `demo123`

## Build for Production

```bash
npm run build
npm run preview  # Preview production build
```

## Docker

```bash
docker build -t pocketllm-frontend .
docker run -p 5173:80 pocketllm-frontend
```

**Note**: Nginx serves the production build on port 80 (mapped to 5173).

## Key Features

- JWT-based authentication
- Server-sent events (SSE) for streaming responses
- Persistent sessions with localStorage
- Real-time chat interface
- Admin dashboard for user management
