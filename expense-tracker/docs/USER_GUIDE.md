# Expense Tracker - User Guide & Feature Flow

This document provides a comprehensive overview of the Expense Tracker application, detailing the complete feature list and the standard user flow through the application.

---

## 1. Feature List

### 🔑 Authentication & Security
- **User Registration**: Secure account creation requiring a strong password (minimum 12 characters, checked against known data breaches).
- **Secure Login**: Authentication using short-lived Access Tokens (JWT) and long-lived Refresh Tokens stored in secure, `HttpOnly` cookies to prevent XSS attacks.
- **Brute-Force Protection**: Automatic account lockout after 5 consecutive failed login attempts, preventing unauthorized access guessing.
- **Persistent Sessions**: Seamless automatic token rotation and renewal in the background so you stay logged in securely without interruptions.

### 💰 Expense Management (Core CRUD)
- **Add Expense**: Log a new transaction with an amount, description, category, and date.
- **View Expenses**: Browse a paginated list of all past transactions.
- **Edit Expense**: Modify existing transactions to correct amounts or categories.
- **Delete Expense**: Remove erroneous or duplicate transactions.

### 📊 Dashboard & Reporting
- **Overview Dashboard**: A high-level landing page providing a summary of financial activity.
- **Categorization**: Expenses are categorized (e.g., Food, Transport, Utilities) for easy tracking and filtering.

### 2.5 Enterprise & Advanced Features (Roadmap)
- **Recurring Expenses**: Automatically log recurring subscriptions (Netflix, Rent) on a schedule.
- **Budgets & Alerts**: Set monthly limits per category and receive warnings before overspending.
- **Advanced Analytics & Export**: Month-over-Month comparisons, heatmaps, and CSV/PDF export.
- **Shared Wallets (Groups)**: Share an expense book with roommates and automatically track who owes whom.
- **Multi-Currency**: Log expenses in any currency and auto-convert to USD using live exchange rates.
- **Split Transactions**: Split a single receipt (e.g., $100 Target) across multiple categories.
- **Tags & Geolocation**: Attach `#tags`, PDF invoices, and GPS coordinates to transactions.

### 🤖 Autonomous Agentic AI
- **Autonomous Financial Advisor**: A LangGraph multi-agent system that can autonomously query your data, analyze spending habits, and execute actions (like setting budgets) via a chat interface.
- **Local RAG (Document Chat)**: Upload bank statements or tax forms and chat with them using local vector databases (ChromaDB) ensuring complete data privacy.
- **Human-in-the-Loop Safety**: The AI graph pauses and requests your explicit approval before executing any destructive actions.
- **Self-Healing Agents**: The AI catches its own errors and re-attempts actions automatically.
- **Voice-to-Action**: Log expenses seamlessly using voice commands (Web Speech API).
- **Receipt Scanning (OCR)**: Upload an image of a receipt to automatically extract the amount, date, and merchant.
- **Receipt Scanning (OCR)**: Upload a picture of a receipt to automatically extract the total amount and date.
- **Data Export**: Download your transaction history as a CSV file for personal record-keeping.

---

## 2. Standard User Flow

### Phase 1: Onboarding
1. **Visit the App**: The user navigates to the application URL. Unauthenticated users are automatically redirected to the **Login Page**, where they can log in using either their username or email address.
2. **Sign Up**: A new user clicks "Sign up", fills out their Username, Email, Optional Full Name, and a strong password on the **Register Page**. Temporary (disposable) emails are blocked to ensure authenticity.
3. **Verify Email**: An OTP is sent to their registered email address. The user enters this OTP to verify their email.
4. **Auto-Login**: Upon successful OTP verification, the user is automatically logged in and securely routed to the **Dashboard**.

### Phase 2: Daily Usage
1. **The Dashboard**: The user lands on the Dashboard where they are greeted and can see a quick summary of their recent activity.
2. **Logging an Expense**: 
   - The user navigates to the "Add Expense" form.
   - They input `$15.50` for `Lunch`, select the category `Food`, and submit.
   - The system validates the input, saves it to the database, and updates the user's dashboard balance.
3. **Reviewing History**: 
   - The user visits the "Transactions" list to view past expenses.
   - They notice a mistake, click "Edit", and correct an amount from `$50` to `$5`.

### Phase 3: Session Management
- **Closing the App**: The user closes the browser tab.
- **Returning Later**: When they return the next day, the frontend automatically securely contacts the backend to renew their session using their secure cookie. They bypass the login screen and land directly on their dashboard.
- **Logging Out**: To secure their device, the user clicks **Logout**. The backend actively revokes their session token and clears the secure cookie, redirecting them back to the Login screen.

---

## 3. Technical Flow (Under the Hood)
1. **Client Request**: React frontend intercepts user actions.
2. **API Interceptor**: The Axios interceptor automatically attaches the `Bearer <Token>` to outgoing requests. If a token is expired, it pauses the request, fetches a new one silently, and retries the request.
3. **Backend Validation**: FastAPI routes validate incoming data using Pydantic schemas.
4. **Data Persistence**: SQLAlchemy async ORM handles secure, parameterized insertion into the PostgreSQL database.
5. **Response**: The frontend receives the response and dynamically updates the React state without a full page reload.
