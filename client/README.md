# ASHA AI Chatbot Frontend

This directory contains the **React** frontend for the ASHA AI Chatbot. It provides the user interface for registration, login, and chatting with the Asha career guidance bot.

---

## 🚀 Features

- **Login & Registration** forms with client-side validation
- **Chat UI** for interacting with the Asha chatbot
- **Responsive Design** using Tailwind CSS (or your chosen framework)
- **Environment-based API proxy** in development for seamless backend integration
- **Production Build** ready for deployment (served by Flask or any static host)

---

## 📦 Prerequisites

- **Node.js** ≥ v18
- **npm** (or **yarn**)
- **Environment Variables** (for production API endpoint)

---

## 🛠 Installation & Development

1. **Navigate to the frontend folder**
   ```bash
   cd client
   ```

2. **Install dependencies**
   ```bash
   npm ci
   # or yarn install
   ```

3. **Development Server**
   ```bash
   npm start
   ```
   - Runs the app in development mode at `http://localhost:3000`
   - The React dev server proxies API requests to the backend (port 5000) via the `proxy` setting in `package.json`.

4. **Environment Variables for Development**
   In `client/.env.development`, you can define variables:
   ```ini
   REACT_APP_API_URL=http://localhost:5000
   ```
   These are automatically loaded by Create React App.

---

## ⚙️ Available Scripts

Inside the `client` directory, you can run:

| Command         | Description                                    |
|-----------------|------------------------------------------------|
| `npm start`     | Starts the development server                  |
| `npm run build` | Builds the app for production into `/build`    |
| `npm test`      | Runs the test suite (if configured)            |
| `npm run eject` | Ejects CRA configuration (one-way operation)   |

---

## 📂 Project Structure

```
client/
├── public/              # Static HTML, manifest, favicon
│   └── index.html       # Main HTML page
├── src/                 # React application source
│   ├── api.js           # API helper (fetch/axios with credentials)
│   ├── components/      # Reusable UI components
│   ├── pages/           # Route-based pages (Login, Register, Chat)
│   ├── App.jsx          # App root and Router setup
│   ├── index.js         # Entry point for ReactDOM
│   └── styles/          # Tailwind or CSS files
├── .env.development     # Dev environment variables
├── package.json         # Project metadata & scripts
└── tailwind.config.js   # (optional) Tailwind CSS configuration
```

---

## 🛡️ API Integration

- All API calls should use the `REACT_APP_API_URL` environment variable.
- Ensure `credentials: 'include'` (or `axios.defaults.withCredentials = true`) is set to allow cookie-based sessions.

Example (`src/api.js`):
```js
const API = process.env.REACT_APP_API_URL;

export async function login(username, password) {
  const res = await fetch(`${API}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ username, password }),
  });
  return res.json();
}
```

---

## 📦 Production Build

1. **Build**
   ```bash
   npm run build
   ```
   - Outputs optimized static files to `client/build`.

2. **Serve Static Files**
   - You can serve `client/build` from any static hosting service (Netlify, Vercel, S3) or let the Flask backend serve it.

---
