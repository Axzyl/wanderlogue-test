# Photo Memory App

A web application that helps you remember your travel photos by identifying locations and providing historical context using AI.

## Features

- Upload multiple travel photos
- AI-powered analysis using Claude (Anthropic)
- Location identification and historical context
- Photo gallery with saved analyses
- User authentication via Clerk

## Tech Stack

- **Frontend**: React + Vite
- **Backend**: Python + FastAPI
- **Database**: PostgreSQL
- **Storage**: DigitalOcean Spaces
- **Auth**: Clerk
- **AI**: Anthropic Claude API
- **Deployment**: DigitalOcean App Platform

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings/configuration
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── routers/
│   │   └── photos.py        # Photo endpoints
│   ├── services/
│   │   ├── auth_service.py  # Clerk authentication
│   │   ├── claude_service.py # Anthropic API
│   │   └── storage_service.py # DO Spaces
│   └── alembic/             # Database migrations
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── components/
│   │       ├── PhotoUpload.jsx
│   │       ├── AnalysisOutput.jsx
│   │       └── Gallery.jsx
│   └── index.html
├── .do/
│   └── app.yaml             # DigitalOcean App spec
├── docker-compose.yml       # Local development
└── .env.example             # Environment template
```

## Setup

### 1. Clone and Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 2. Get Required API Keys

#### Anthropic API Key
1. Go to https://console.anthropic.com/
2. Create an API key
3. Add to `.env` as `ANTHROPIC_API_KEY`

#### Clerk Authentication
1. Go to https://dashboard.clerk.com/
2. Create a new application
3. Copy the Publishable Key and Secret Key
4. Add to `.env`:
   - `CLERK_PUBLISHABLE_KEY`
   - `CLERK_SECRET_KEY`
   - `VITE_CLERK_PUBLISHABLE_KEY` (same as publishable key)

#### DigitalOcean Spaces
1. Go to DigitalOcean Control Panel > Spaces
2. Create a new Space (bucket)
3. Go to API > Spaces Keys
4. Generate new key
5. Add to `.env`:
   - `DO_SPACES_KEY`
   - `DO_SPACES_SECRET`
   - `DO_SPACES_BUCKET` (your bucket name)

### 3. Local Development

#### Option A: Docker Compose (Recommended)
```bash
docker-compose up --build
```
- Frontend: http://localhost:80
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

#### Option B: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Deployment to DigitalOcean

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/photo-memory-app.git
git push -u origin main
```

### 2. Create DigitalOcean Resources

1. **Create a Space** for photo storage
2. **Create a Managed Database** (PostgreSQL)

### 3. Deploy via App Platform

1. Go to DigitalOcean App Platform
2. Connect your GitHub repository
3. Configure environment variables in the App settings
4. Deploy!

Or use the CLI:
```bash
# Update .do/app.yaml with your GitHub repo
doctl apps create --spec .do/app.yaml
```

### Environment Variables for Production

Set these in DigitalOcean App Platform:

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `CLERK_SECRET_KEY` | Clerk secret key |
| `CLERK_PUBLISHABLE_KEY` | Clerk publishable key |
| `DO_SPACES_KEY` | Spaces access key |
| `DO_SPACES_SECRET` | Spaces secret key |
| `DO_SPACES_BUCKET` | Your Space name |
| `DATABASE_URL` | PostgreSQL connection string |
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk publishable key (build-time) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/photos/upload` | Upload photos |
| POST | `/api/photos/{id}/analyze` | Analyze a photo |
| POST | `/api/photos/analyze-batch` | Analyze multiple photos |
| GET | `/api/photos/` | List all user photos |
| GET | `/api/photos/{id}` | Get photo details |
| DELETE | `/api/photos/{id}` | Delete a photo |

## License

MIT
