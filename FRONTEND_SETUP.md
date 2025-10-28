# Frontend Setup Guide - Multi-User Job Manager

## Overview
The frontend has been updated with a complete authentication system including:
- Login and Registration pages
- Protected routes
- User preferences management (Settings page)
- JWT-based authentication
- User info display in sidebar
- Logout functionality

## Prerequisites
- Node.js 18+ and npm installed
- Backend API running (Railway or local)
- Database migrated with multi-user schema

## Installation

### 1. Navigate to Frontend Directory
```bash
cd job-manager-ui
```

### 2. Install Dependencies
```bash
npm install
```

This will install all required packages including:
- React Router DOM (for routing)
- Material-UI components
- Axios (for API calls)
- React Hot Toast (for notifications)

### 3. Configure Environment Variables

Create a `.env` file in the `job-manager-ui` directory:

```env
VITE_API_URL=http://localhost:8000
```

**For production (Railway):**
```env
VITE_API_URL=https://your-railway-url.railway.app
```

### 4. Run Development Server
```bash
npm run dev
```

The app will open at `http://localhost:5173`

## Testing the Authentication Flow

### 1. Register a New User
1. Navigate to `http://localhost:5173` (will redirect to `/login`)
2. Click "Sign up" link at the bottom
3. Fill in registration form:
   - Username (min 3 characters)
   - Email (valid email format)
   - Full Name (optional)
   - Password (min 8 characters, must include letters and numbers)
   - Confirm Password
4. Click "Create Account"
5. You'll be automatically logged in and redirected to dashboard

### 2. Test Login
1. Logout using the red "Logout" button in sidebar
2. You'll be redirected to `/login`
3. Enter your username and password
4. Click "Sign In"
5. You'll be redirected to the dashboard

### 3. Configure Preferences
1. Click "Settings" in the sidebar
2. Configure your job preferences:
   - **Job Types:** software, hr, marketing, design, data, sales
   - **Experience Levels:** entry, junior, mid, senior, executive
   - **Preferred Countries:** Ireland, Spain, Panama, Chile, Netherlands, Germany, Sweden, Remote
   - **Keywords (Include):** Technologies or terms you want to see
   - **Excluded Keywords:** Terms to filter out (e.g., Senior, Lead, Manager)
   - **Preferred Cities:** Specific cities (optional)
   - **Excluded Companies:** Companies to filter out
   - **Filters:**
     - Easy Apply only (LinkedIn Easy Apply jobs)
     - Remote jobs only
3. Click "Save Preferences"

### 4. Test Protected Routes
- Try accessing `/settings` without logging in → redirects to `/login`
- Try accessing `/` without logging in → redirects to `/login`
- After login, try accessing `/login` → redirects to `/` (dashboard)

## File Structure

```
job-manager-ui/src/
├── pages/
│   ├── LoginPage.tsx          # User login
│   ├── RegisterPage.tsx       # New user registration
│   └── SettingsPage.tsx       # User preferences
├── contexts/
│   └── AuthContext.tsx        # Authentication state management
├── services/
│   └── authService.ts         # Authentication API calls
├── components/
│   └── ProtectedRoute.tsx     # Route protection wrapper
├── AppRouter.tsx              # Route definitions
├── main.tsx                   # Entry point with AuthProvider
└── App.tsx                    # Main dashboard (protected)
```

## Key Features

### Authentication Context
The `AuthContext` provides:
- `user`: Current user object (username, email, etc.)
- `preferences`: User job preferences
- `isAuthenticated`: Boolean authentication status
- `login(username, password)`: Login function
- `register(...)`: Registration function
- `logout()`: Logout function
- `updatePreferences(prefs)`: Update user preferences

### Protected Routes
Routes are protected using `ProtectedRoute` component:
- Redirects to `/login` if not authenticated
- Shows loading spinner while checking auth
- Allows access if authenticated

### API Integration
All API calls use JWT tokens stored in `localStorage`:
- Token is automatically included in request headers
- Token is validated on each request
- Expired tokens redirect to login

## Backend API Endpoints Used

- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Authenticate user
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/preferences` - Get user preferences
- `PUT /api/auth/preferences` - Update preferences
- `POST /api/auth/logout` - Logout user

## Common Issues

### 1. "Failed to fetch" or CORS errors
**Solution:** Ensure backend is running and `VITE_API_URL` is correct

### 2. "Network Error: Unable to connect to API"
**Solution:** Check if Railway backend is deployed and URL is correct

### 3. Token expired errors
**Solution:** Just logout and login again (tokens expire after 7 days)

### 4. React Router warnings
**Solution:** Ensure you're using `navigate()` for programmatic navigation, not `<Link>`

## Build for Production

```bash
npm run build
```

This creates optimized production files in `dist/` directory.

## Deployment

The frontend can be deployed to:
- **Vercel** (recommended for React apps)
- **Netlify**
- **Railway** (static site)
- **GitHub Pages**

Make sure to set `VITE_API_URL` environment variable to your production backend URL.

## User Management

### Creating Users via Script

You can also create users programmatically using the backend scripts:

```bash
# Create the admin user (User 1)
python migrate_existing_user_data.py

# Create HR user (User 2)
python create_hr_user.py
```

### Default Admin Account
If you ran `migrate_existing_user_data.py`:
- **Username:** `admin`
- **Password:** `admin123`
- **Email:** `admin@jobmanager.local`

### Default HR Account
If you ran `create_hr_user.py`:
- **Username:** `hr_user`
- **Password:** `hr123`
- **Email:** `hr@jobmanager.local`

## Next Steps

1. **Phase 2:** Implement user-specific job filtering
   - Filter jobs based on user preferences
   - Show only relevant jobs per user
   - Separate applied/rejected tracking per user

2. **Enhancements:**
   - Password reset functionality
   - Email verification
   - Profile picture upload
   - Advanced filtering options
   - Job recommendations based on preferences

## Support

For issues or questions:
1. Check console logs in browser DevTools
2. Check backend logs for API errors
3. Verify database migration completed successfully
4. Ensure all environment variables are set correctly
