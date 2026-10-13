# Clerk Authentication

A complete, production-ready web application built with **Python**, **Streamlit**, and **Clerk Authentication**.

This project implements end-to-end user authentication, cryptographic session token and live session validation, protected page routing, and secure session revocation with Clerk.

---

## 🌟 Architecture & Workflow

```text
                  Clerk Authentication
                          │
                          ▼
                   Start Streamlit
                          │
                          ▼
              Check Clerk Authentication
                          │
                ┌─────────┴─────────┐
                │                   │
          Not Logged In         Logged In
                │                   │
                ▼                   ▼
           Sign-In Page         Home Page
                │               Dashboard
                ▼                   │
          Clerk Sign-In             │
                │                   │
                ▼                   │
     Authentication Successful      │
                │                   │
                ▼                   │
       Validate Clerk Session       │
       & Retrieve User Info         │
                │                   │
                └─────────► Home ◄──┘
                             │
                             ▼
                          Sign Out
                             │
                             ▼
                     End Clerk Session
                    (Backend Revocation)
                             │
                             ▼
                        Sign-In Page
```

---

## 🛠️ Features

* **Real Clerk Authentication:** Integrates with Clerk's Frontend UI (`@clerk/clerk-js`) and the official `clerk-backend-api` Python SDK.
* **Strict Session Gate:** Protected views (Home, Dashboard, Profile) are physically gated behind Clerk backend session verification. `st.session_state` is never trusted in isolation without Clerk validation.
* **Live Session & Token Verification:** Validates session status (`active`, expiration time) and verifies JWT tokens against Clerk's JWKS public keys.
* **Complete User Profile:** Automatically pulls verified user information (display name, email addresses, avatar image, account creation date, 2FA status) directly from Clerk.
* **Working Sign Out:** Revokes the session on Clerk's backend via `clerk.sessions.revoke()`, clears local session state, and redirects to the sign-in page.
* **Modern Streamlit Dashboard:** Custom cards, responsive design, dark mode theme, and sleek navigation sidebar.

---

## 📁 Project Structure

```text
clerk/
│
├── app.py                      # Main application entry point & authentication gate
│
├── pages/
│   ├── home.py                 # Protected Home page
│   └── profile.py              # Protected Profile page
│
├── components/
│   ├── auth.py                 # Sign-in UI, key configuration guide & direct session validation
│   ├── sidebar.py              # Sidebar navigation, user identity card & Sign Out action
│   ├── dashboard.py            # Dashboard metrics, welcome banner & status cards
│   └── clerk_component/
│       └── index.html          # Embedded ClerkJS custom component
│
├── services/
│   └── clerk_service.py        # Clerk SDK service (validation, user retrieval, session revocation)
│
├── utils/
│   └── session.py              # Session management, authentication checks, and protection guards
│
├── .streamlit/
│   └── config.toml             # Streamlit configuration, theme & navigation settings
│
├── .env                        # Local environment variables (ignored by Git)
├── .env.example                # Example environment variable template
├── .gitignore                  # Git ignore rules protecting secrets
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites

* **Python 3.10+** (tested up to Python 3.14)
* A free [Clerk account](https://dashboard.clerk.com)

### 2. Set Up a Virtual Environment

```bash
# Clone or navigate to the project directory
cd clerk

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Windows (CMD):
.\venv\Scripts\activate.bat

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Clerk Configuration & Environment Variables

1. Go to the [Clerk Dashboard](https://dashboard.clerk.com).
2. Create an application (or select an existing one).
3. In the left sidebar, navigate to **Configure > Developers > API Keys**.
4. Copy the **Publishable key** (`pk_test_...`) and the **Secret key** (`sk_test_...`).
5. Create a `.env` file in the project root (or copy `.env.example`):

```bash
cp .env.example .env
```

6. Open `.env` and fill in your keys:

```env
# Clerk Publishable Key (used by browser ClerkJS)
CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here

# Clerk Secret Key (server-side only, NEVER exposed to browser)
CLERK_SECRET_KEY=sk_test_your_secret_key_here
```

> **Security Note:** `.env` is listed in `.gitignore` to prevent committing your secret keys. `CLERK_SECRET_KEY` is strictly used by Python on the server side and is never sent to the browser or rendered in HTML.

---

## ▶️ Running the Application

Start the Streamlit application using:

```bash
streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`.

---

## 🔒 Authentication Flow in Action

1. **Unauthenticated State:**
   * When opening the app, the session check detects no authenticated user.
   * The Sign-In screen appears with the Clerk authentication card.
   * The protected dashboard cannot be accessed.

2. **Sign-In:**
   * Sign in using your email/password or OAuth provider in the Clerk interface.
   * Upon successful sign-in, the session token and session ID are sent to the Python backend.
   * The Python backend verifies the session with Clerk API and loads the verified user record.
   * The application automatically transitions to the **Home Dashboard**.

3. **Protected Dashboard:**
   * Displays personalized header: **Welcome, [User Name]**, user avatar, and email.
   * Displays 4 status cards:
     * **Authentication Status**
     * **User Profile**
     * **Account Information**
     * **Application Status**
   * Features a live session inspector and security controls.

4. **Sign Out:**
   * Click **🚪 Sign Out** in the sidebar or dashboard.
   * The session is revoked on Clerk's backend via `clerk.sessions.revoke()`.
   * Local session state is cleared.
   * The application immediately redirects back to the **Sign-In** screen.

---

## 🛡️ Security Verification

* **Server-side Session Validation:** All requests to protected screens verify the session with Clerk's live servers.
* **Token Tampering Prevention:** Altering Streamlit's `st.session_state` fails backend validation and triggers an immediate redirect.
* **Credential Hygiene:** No API keys or tokens are hardcoded or printed in logs.
