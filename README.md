# PTT Site Watcher

A full-stack application to monitor PTT (Turkish Postal Service) announcements for changes. The backend uses Python Flask with Playwright for web scraping and SQLite for persistence. The frontend uses React + TypeScript + Tailwind CSS.

## Features

- 🔍 **Automated Scraping**: Uses Playwright to scrape PTT announcements page
- 📊 **Change Detection**: Tracks new, modified, and removed announcements
- 💾 **Persistent Storage**: SQLite database for storing announcement history
- 🎨 **Modern UI**: Dark theme with glassmorphism effects
- 🔄 **Real-time Updates**: Auto-polling during scans

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **npm**

## Quick Start

### Backend Setup

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Start the server
python app.py
```

The API will be available at `http://localhost:5000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The UI will be available at `http://localhost:5173`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | Get scan status and stats |
| GET | `/api/announcements` | List all tracked announcements |
| GET | `/api/changes` | List detected changes |
| POST | `/api/scan` | Trigger a new scan |
| GET | `/api/health` | Health check |

## Environment Configuration

Copy `.env.example` to `.env` in the backend folder:

```bash
cp backend/.env.example backend/.env
```

Available options:

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | development | Flask environment |
| `FLASK_DEBUG` | 1 | Enable debug mode |
| `DATABASE_PATH` | ptt_watcher.db | SQLite database file |
| `PTT_URL` | (see file) | Target URL to scrape |
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 5000 | Server port |

## Project Structure

```
site-watcher/
├── backend/
│   ├── app.py              # Flask API server
│   ├── scraper.py          # Playwright scraper
│   ├── database.py         # SQLite operations
│   ├── models.py           # Data models
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment config example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── StatusIndicator.tsx
│   │   │   ├── ScanButton.tsx
│   │   │   ├── AnnouncementList.tsx
│   │   │   └── ChangeLog.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── index.css
│   ├── tailwind.config.js
│   └── package.json
└── README.md
```

## Usage

1. Start the backend server
2. Start the frontend development server
3. Open `http://localhost:5173` in your browser
4. Click **"Scan Now"** to fetch announcements
5. View tracked announcements and change history

## License

MIT
