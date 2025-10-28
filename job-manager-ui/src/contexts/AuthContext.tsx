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
        try {
          // Verify token is still valid by fetching user
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);

          // Load preferences
          const prefs = await authService.getPreferences();
          setPreferences(prefs);
        } catch (error) {
          console.error('Token expired or invalid:', error);
          // Clear invalid token
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          setUser(null);
        }
      }

      setIsLoading(false);
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
      const response = await authService.register(username, email, password, fullName);
      setUser(response.user);

      // Load preferences after registration
      const prefs = await authService.getPreferences();
      setPreferences(prefs);

      toast.success(`Welcome, ${response.user.username}!`);
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Registration failed';
      toast.error(message);
      throw error;
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
    logout,
    refreshUser,
    refreshPreferences,
    updatePreferences,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
