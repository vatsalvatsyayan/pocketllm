# pocketLLM Frontend - Development Guide

Quick reference for developing the chat interface.

---

## 🚀 Quick Start

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

**Login:** `demo@pocketllm.com` / `demo123`

---

## 🎭 Mock vs Real API

### Currently Using: **Mock Services** ✅

Everything works without a backend!

**Switch modes in `.env.local`:**
```env
VITE_MOCK_CHAT=true   # Mock (current)
VITE_MOCK_CHAT=false  # Real backend (needs API running)
```

---

## 📁 Project Structure

```
src/
├── components/chat/     # Chat UI components
│   ├── MessageBubble    # Individual messages
│   ├── Composer         # Input box
│   ├── ChatThread       # Message list
│   └── SessionList      # Sidebar
├── pages/
│   └── ChatPage.tsx     # Main chat orchestrator
├── services/
│   ├── chat/
│   │   ├── index.ts           # Auto-switches mock/real
│   │   ├── chatService.ts     # Real API (ready)
│   │   ├── mockChatService.ts # Mock sessions
│   │   └── mockStreamService.ts # Mock streaming
│   └── auth/            # Authentication
├── hooks/
│   └── useChatStream.ts # Streaming logic
└── types/
    └── chat.types.ts    # TypeScript definitions
```

---

## 🎯 Features Implemented

✅ Session management (create, list, delete)
✅ Message history
✅ Real-time streaming (token-by-token)
✅ Cancel streaming
✅ Auto-scroll
✅ Auto-title generation
✅ Optimistic updates
✅ Error handling
✅ Mock TinyLlama responses

---

## 🔧 Backend Requirements

When ready to connect real backend:

### Endpoints Needed:
```
GET    /api/chat/sessions              # List sessions
POST   /api/chat/sessions              # Create session
GET    /api/chat/sessions/:id          # Get session
PATCH  /api/chat/sessions/:id          # Update session
DELETE /api/chat/sessions/:id          # Delete session
GET    /api/chat/sessions/:id/messages # Get messages
POST   /api/chat/stream                # Stream LLM (SSE)
```

### Request/Response Formats:

**Stream Request:**
```json
POST /api/chat/stream
{
  "sessionId": "session_123",
  "prompt": "user question",
  "messageId": "msg_456"
}
```

**Stream Response (SSE):**
```
data: {"type":"token","content":"Hello"}
data: {"type":"token","content":" world"}
data: {"type":"end","messageId":"msg_456"}
```

**Session Response:**
```json
{
  "id": "session_123",
  "userId": "user_456",
  "title": "Chat Title",
  "createdAt": "2025-11-17T10:00:00Z",
  "updatedAt": "2025-11-17T10:05:00Z",
  "messageCount": 4
}
```

---

## 🧪 Testing

**Mock Mode Tests:**
1. Login → Create chat → Send message → See streaming
2. Click stop → Verify message saved
3. Switch sessions → Messages persist
4. Delete session → Removed from list

**Console Logs:**
```javascript
🎭 Using MOCK chat service  # Mock enabled
🚀 Mock Stream: Starting... # Streaming
✅ Persisted messages       # Saved
```

---

## 🐛 Troubleshooting

**Messages disappear:**
- Ensure `VITE_MOCK_CHAT=true` in `.env.local`
- Restart dev server: `npm run dev`

**Streaming not working:**
- Check browser console for errors
- Verify mock service logs appear

**Port 5173 in use:**
```bash
lsof -ti:5173 | xargs kill -9
npm run dev
```

---

## 📚 Key Files

**Main Logic:**
- `ChatPage.tsx` - State management, message flow
- `useChatStream.ts` - Streaming handler
- `chatService.ts` - API calls

**Mock Services:**
- `mockChatService.ts` - Sessions & messages
- `mockStreamService.ts` - TinyLlama responses

**Configuration:**
- `.env.local` - Environment variables
- `constants.ts` - App configuration

---

## 🎨 Tech Stack

- React 18 + TypeScript
- Vite (build tool)
- React Router 6 (routing)
- Tailwind CSS (styling)
- Lucide React (icons)

---

## 📝 Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_AUTH_TOKEN_KEY=pocketllm_auth_token
VITE_MOCK_AUTH=true
VITE_MOCK_CHAT=true
VITE_APP_NAME=pocketLLM Portal
```

---

## 🚀 Deployment

**Build for production:**
```bash
npm run build
# Output in dist/
```

**Before deploying:**
- Set `VITE_MOCK_CHAT=false`
- Set correct `VITE_API_BASE_URL`
- Ensure backend is running

---

**Questions?** Check `README.md` for full details.

