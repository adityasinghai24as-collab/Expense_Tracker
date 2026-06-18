# Expense Tracker - Cloudflare Monorepo

A minimalist full-stack monorepo template for Cloudflare Workers, built with FastAPI (Python) backend and Vite + React frontend.

## Project Structure

```
expense-tracker/
├── backend/
│   ├── main.py           # FastAPI application with health check endpoint
│   ├── requirements.txt   # Python dependencies
│   └── wrangler.toml      # Cloudflare Workers configuration
├── frontend/
│   ├── package.json       # Node dependencies and scripts
│   ├── vite.config.js     # Vite configuration
│   ├── tailwind.config.js # Tailwind CSS configuration
│   ├── postcss.config.js  # PostCSS configuration
│   ├── index.html         # HTML entry point
│   └── src/
│       ├── main.jsx       # React entry point
│       ├── App.jsx        # Root component with connection status display
│       └── index.css      # Global styles with Tailwind directives
└── README.md              # This file
```

## Quick Start

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000` with docs at `http://localhost:8000/docs`

4. For Cloudflare Workers deployment:
   ```bash
   wrangler deploy
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   The frontend will open at `http://localhost:5173`

4. Build for production:
   ```bash
   npm run build
   ```

## API Endpoints

- **GET `/health`** - Health check endpoint
  ```json
  {
    "status": "ok",
    "message": "Expense Tracker API is running"
  }
  ```

## Frontend Features

- **React 18** with modern hooks
- **Vite** for fast development and optimized builds
- **Tailwind CSS** for utility-first styling
- **Automatic API proxy** from `/api/*` to backend
- **Connection status monitor** showing backend health

## Configuration

### Backend (wrangler.toml)

- Python Workers enabled via `compatibility_flags = [ "python_workers" ]`
- Uncomment the Hyperdrive section to add database connectivity
- Add environment-specific configuration under `[env.production]`

### Frontend (vite.config.js)

- API proxy configured to forward `/api/*` requests to backend
- Development server runs on port 5173
- Build output goes to `dist/`

## Deployment

### Cloudflare Workers (Backend)

```bash
cd backend
wrangler deploy
```

### Cloudflare Pages (Frontend)

```bash
cd frontend
npm run build
# Deploy the dist/ folder to Cloudflare Pages
```

## Next Steps

1. **Backend**: Implement expense tracking logic in `main.py`
2. **Frontend**: Build UI components for expense management
3. **Database**: Uncomment Hyperdrive in `wrangler.toml` and add your database schema
4. **Authentication**: Add user authentication and authorization
5. **Testing**: Add pytest tests for backend and Jest for frontend

## Environment Variables

Create `.env` or `.env.local` files in respective directories for local development.

- **Backend**: Add environment variables in `wrangler.toml` under `[env.production.vars]`
- **Frontend**: Prefix with `VITE_` to expose variables to the frontend

## License

MIT
