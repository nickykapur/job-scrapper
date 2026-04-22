/**
 * Authentication Context
 * Provides authentication state and methods throughout the app
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import authService, { User, UserPreferences } from '../services/authService';
import toast from 'react-hot-toast';

interface AuthContextType {
  user: User | null;
  preferences: UserPreferences | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, fullName?: string) => Promise<void>;
  registerQuick: (email: string, fullName?: string) => Promise<{ default_password: string }>;
  finalizeAuth: () => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  refreshPreferences: () => Promise<void>;
  updatePreferences: (prefs: Partial<UserPreferences>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  // Load user on mount
  useEffect(() => {
    const initAuth = async () => {
      const storedUser = authService.getStoredUser();
      const token = authService.getToken();

      if (storedUser && token) {
        // Show the app immediately using cached data — no spinner for returning users
        setUser(storedUser);
        setIsLoading(false);

        // Verify token + refresh data in the background
        try {
          const [currentUser, prefs] = await Promise.all([
            authService.getCurrentUser(),
            authService.getPreferences(),
          ]);
          setUser(currentUser);
          setPreferences(prefs);
        } catch (error) {
          // Token expired — clear and send to landing page
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          setUser(null);
        }
      } else {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await authService.login(username, password);
      setUser(response.user);

      // Load preferences after login
      const prefs = await authService.getPreferences();
      setPreferences(prefs);

      toast.success(`Welcome back, ${response.user.username}!`);
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed';
      toast.error(message);
      throw error;
    }
  };

  const register = async (username: string, email: string, password: string, fullName?: string) => {
    try {
      // Store token but do NOT set user state yet — the RegisterPage needs to show
      // step 2 (onboarding) before AppRouter redirects away.
      await authService.register(username, email, password, fullName);
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Registration failed';
      toast.error(message);
      throw error;
    }
  };

  const registerQuick = async (email: string, fullName?: string) => {
    try {
      const res = await authService.registerQuick(email, fullName);
      // Set user state so AppRouter treats them as authenticated and
      // redirects them straight into the onboarding flow.
      setUser({ ...res.user, onboarding_completed: false });
      return { default_password: res.default_password };
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Registration failed';
      toast.error(message);
      throw error;
    }
  };

  // Called by RegisterPage after onboarding step 2 is complete.
  // Sets user state which triggers AppRouter to redirect to the dashboard.
  const finalizeAuth = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
      const prefs = await authService.getPreferences();
      setPreferences(prefs);
      toast.success(`Welcome, ${currentUser.username}!`);
    } catch (error) {
      console.error('finalizeAuth failed:', error);
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
      setUser(null);
      setPreferences(null);
      toast.success('Logged out successfully');
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear local state even if API call fails
      setUser(null);
      setPreferences(null);
    }
  };

  const refreshUser = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error('Failed to refresh user:', error);
      throw error;
    }
  };

  const refreshPreferences = async () => {
    try {
      const prefs = await authService.getPreferences();
      setPreferences(prefs);
    } catch (error) {
      console.error('Failed to refresh preferences:', error);
      throw error;
    }
  };

  const updatePreferences = async (prefs: Partial<UserPreferences>) => {
    try {
      await authService.updatePreferences(prefs);
      // Refresh preferences after update
      await refreshPreferences();
      toast.success('Preferences updated successfully');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to update preferences';
      toast.error(message);
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    preferences,
    isAuthenticated,
    isLoading,
    login,
    register,
    registerQuick,
    finalizeAuth,
    logout,
    refreshUser,
    refreshPreferences,
    updatePreferences,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
