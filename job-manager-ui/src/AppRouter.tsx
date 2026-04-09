/**
 * App Router
 * Handles all application routing and route protection
 */

import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import { Loader2 } from 'lucide-react';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

// Lazy-load the dashboard — keeps MUI + Recharts out of the landing page bundle
const App = React.lazy(() => import('./App'));

const AppFallback = () => (
  <div className="flex justify-center items-center min-h-screen">
    <Loader2 className="h-8 w-8 animate-spin text-primary" />
  </div>
);
// import SettingsPage from './pages/SettingsPage'; // Temporarily disabled - MUI migration pending
import ProtectedRoute from './components/ProtectedRoute';

const AppRouter: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <Routes>
      {/* Public routes - redirect to dashboard if already authenticated */}
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />}
      />
      <Route
        path="/register"
        element={isAuthenticated ? <Navigate to="/" replace /> : <RegisterPage />}
      />

      {/* Home: landing page for guests, dashboard for authenticated users */}
      <Route
        path="/"
        element={
          isAuthenticated ? (
            <ProtectedRoute>
              <Suspense fallback={<AppFallback />}><App /></Suspense>
            </ProtectedRoute>
          ) : (
            <LandingPage />
          )
        }
      />
      {/* Temporarily disabled - MUI migration pending
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        }
      />
      */}

      {/* Catch all - redirect to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRouter;
