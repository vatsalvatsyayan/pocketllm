# pocketLLM Portal - Quick Start Guide

## 🚀 Running the Application

### Start Development Server
```bash
cd frontend
npm run dev
```

Then open your browser to: **http://localhost:5173**

### Demo Login
```
Email: demo@pocketllm.com
Password: demo123
```

Or create a new account on the signup page!

## 📁 Project Overview

This is a complete authentication system with:
- ✅ Login & Signup pages
- ✅ Protected routes
- ✅ Session persistence
- ✅ Mock authentication (easy to swap with real API)
- ✅ Professional UI with pocketLLM theme
- ✅ Full TypeScript support
- ✅ Responsive design

## 🎯 Key Files

### Pages
- `src/pages/Login.tsx` - Login page
- `src/pages/Signup.tsx` - Signup page
- `src/pages/Dashboard.tsx` - Protected dashboard

### Auth System
- `src/services/auth/mockAuthService.ts` - Mock authentication
- `src/services/auth/index.ts` - **Switch mock/real API here**
- `src/context/AuthContext.tsx` - Global auth state

### UI Components
- `src/components/ui/` - Reusable components (Button, Input, Card, etc.)
- `src/components/auth/` - Auth-specific components
- `src/components/layout/` - Page layouts

## 🔄 Switching to Real API

See `README.md` section "How to Swap Mock Auth with Real API" for detailed instructions.

Quick version:
1. Create `src/services/auth/apiAuthService.ts`
2. Update `src/services/auth/index.ts` export
3. Update `.env.local` with real API URL

## 📚 Full Documentation

See `README.md` for:
- Complete architecture explanation
- API contracts
- Environment variables
- Deployment guide
- Best practices

See `login_signup_plan.md` for:
- Implementation plan
- Design decisions
- Future enhancements

## 🎨 Customization

### Colors
Edit `tailwind.config.js` to change the pocketLLM color scheme

### Components
All reusable components are in `src/components/ui/`

### Validation Rules
Edit `src/utils/constants.ts` and `src/utils/validation.ts`

## 🏗️ Build for Production

```bash
npm run build
```

Output in `dist/` folder, ready for deployment!
