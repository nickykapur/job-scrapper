/**
 * Authentication Service
 * Handles all auth-related API calls
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api/auth';

export interface User {
  user_id: number;
  username: string;
  email: string;
  full_name?: string;
  is_admin: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface UserPreferences {
  job_types: string[];
  keywords: string[];
  excluded_keywords: string[];
  experience_levels: string[];
  exclude_senior: boolean;
  preferred_countries: string[];
  preferred_cities: string[];
  exclude_locations: string[];
  excluded_companies: string[];
  preferred_companies: string[];
  easy_apply_only: boolean;
  remote_only: boolean;
  email_notifications: boolean;
  daily_digest: boolean;
}

export interface UserStats {
  user_id: number;
  applied_jobs: number;
  rejected_jobs: number;
  saved_jobs: number;
  hidden_jobs: number;
}

class AuthService {
  private getAuthHeader() {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  /**
   * Register a new user
   */
  async register(username: string, email: string, password: string, fullName?: string): Promise<LoginResponse> {
    const response = await axios.post(`${API_URL}/register`, {
      username,
      email,
      password,
      full_name: fullName,
    });

    // Save token to localStorage
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));

    return response.data;
  }

  /**
   * Login user
   */
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await axios.post(`${API_URL}/login`, {
      username,
      password,
    });

    // Save token to localStorage
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));

    return response.data;
  }

  /**
   * Logout user
   */
  async logout() {
    try {
      await axios.post(`${API_URL}/logout`, {}, {
        headers: this.getAuthHeader(),
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage regardless of API call result
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    }
  }

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<User> {
    const response = await axios.get(`${API_URL}/me`, {
      headers: this.getAuthHeader(),
    });
    return response.data;
  }

  /**
   * Get user preferences
   */
  async getPreferences(): Promise<UserPreferences> {
    const response = await axios.get(`${API_URL}/preferences`, {
      headers: this.getAuthHeader(),
    });
    return response.data;
  }

  /**
   * Update user preferences
   */
  async updatePreferences(preferences: Partial<UserPreferences>): Promise<void> {
    await axios.put(`${API_URL}/preferences`, preferences, {
      headers: this.getAuthHeader(),
    });
  }

  /**
   * Get user statistics
   */
  async getStats(): Promise<UserStats> {
    const response = await axios.get(`${API_URL}/stats`, {
      headers: this.getAuthHeader(),
    });
    return response.data;
  }

  /**
   * Change password
   */
  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await axios.post(`${API_URL}/change-password`, {
      old_password: oldPassword,
      new_password: newPassword,
    }, {
      headers: this.getAuthHeader(),
    });
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    return !!token;
  }

  /**
   * Get stored user
   */
  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }

  /**
   * Get access token
   */
  getToken(): string | null {
    return localStorage.getItem('access_token');
  }
}

export default new AuthService();
