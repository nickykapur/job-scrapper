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
import OnboardingPage from './pages/OnboardingPage';

// Lazy-load the dashboard — keeps MUI + Recharts out of the landing page bundle
const App = React.lazy(() => import('./App'));

const AppFallback = () => (
  <div className="flex justify-center items-center min-h-screen">
    <Loader2 className="h-8 w-8 animate-spin text-primary" />
  </div>
);
// import SettingsPage from './pages/SettingsPage'; // Temporarily disabled - MUI migration pending
import ProtectedRoute from './components/ProtectedRoute';

// Admin usernames that can access the main app even without completing onboarding.
// Everyone else is forced through /onboarding on first login.
const ADMIN_USERNAMES = new Set(['admin', 'software_admin', 'sales']);

const needsOnboarding = (user: any): boolean => {
  if (!user) return false;
  if (user.is_admin) return false;
  if (ADMIN_USERNAMES.has(user.username)) return false;
  return user.onboarding_completed === false;
};

const AppRouter: React.FC = () => {
  const { isAuthenticated, isLoading, user } = useAuth();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  const mustOnboard = needsOnboarding(user);

  // Note: we intentionally do NOT force-redirect authenticated-but-mid-onboarding
  // users to /onboarding on every visit. Onboarding is reached only via the
  // explicit navigate() in RegisterPage right after sign-up. Anything else
  // (direct URL, login, return visit) lands on the normal landing/dashboard.

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

      {/* Onboarding — only available to authenticated users who haven't finished it */}
      <Route
        path="/onboarding"
        element={
          !isAuthenticated
            ? <Navigate to="/register" replace />
            : mustOnboard
              ? <OnboardingPage />
              : <Navigate to="/" replace />
        }
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
