/**
 * App Component
 *
 * Main application component with routing configuration.
 * Defines all routes and authentication flow.
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';
import { NotFound } from './pages/NotFound';
import { AdminDashboard } from './pages/AdminDashboard';
import { ROUTES } from './utils/constants';

// Import ChatPage
import { ChatPage } from './pages/ChatPage';

/**
 * Main App component
 */
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* ========== Public Routes ========== */}
          <Route path={ROUTES.LOGIN} element={<Login />} />
          <Route path={ROUTES.SIGNUP} element={<Signup />} />

          {/* ========== Protected Routes ========== */}
          
          {/* Chat Routes - Main feature */}
          <Route
            path={ROUTES.CHAT}
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/chat/:sessionId"
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            }
          />


          {/* Legacy Dashboard - Redirect to chat */}
          <Route
            path={ROUTES.DASHBOARD}
            element={<Navigate to={ROUTES.CHAT} replace />}
          />

          {/* Admin Dashboard */}
          <Route
            path={ROUTES.ADMIN}
            element={
              <ProtectedRoute>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />

          {/* ========== Redirects ========== */}
          
          {/* Root redirect - go to chat (main feature) */}
          <Route path={ROUTES.HOME} element={<Navigate to={ROUTES.CHAT} replace />} />

          {/* ========== 404 Not Found ========== */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
