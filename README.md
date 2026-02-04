# URL Shortener API

A simple URL shortening service built with FastAPI and PostgreSQL.

## Features

- Shorten long URLs to short, shareable links
- Track click statistics for each shortened URL
- View recent click details (IP, user agent, referer)

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the database

Copy the example environment file and update it with your database credentials:

```bash
cp .env.example .env
```

Edit `.env` and set your `DATABASE_URL`:

```
DATABASE_URL=postgresql://user:password@host:port/database
```

### 4. Run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check

```
GET /
```

Returns a welcome message to verify the API is running.

**Response:**
```json
{"message": "URL Shortener API"}
```

### Shorten a URL

```
POST /api/shorten
```

Create a shortened URL.

**Request body:**
```json
{"url": "https://example.com/very/long/url/that/needs/shortening"}
```

**Response:**
```json
{
    "short_code": "abc123",
    "short_url": "http://localhost:8000/abc123",
    "original_url": "https://example.com/very/long/url/that/needs/shortening",
    "created_at": "2024-01-15T10:30:00"
}
```

### Redirect to Original URL

```
GET /{short_code}
```

Redirects to the original URL. Also records click analytics.

**Example:** Visiting `http://localhost:8000/abc123` redirects to the original URL.

### Get URL Statistics

```
GET /api/stats/{short_code}
```

Get click statistics for a shortened URL.

**Response:**
```json
{
    "short_code": "abc123",
    "original_url": "https://example.com",
    "click_count": 42,
    "recent_clicks": [
        {
            "clicked_at": "2024-01-15T12:00:00",
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0...",
            "referer": "https://google.com"
        }
    ]
}
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
url-shortener/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app entry point
│   ├── database.py      # Database connection
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   └── routes/
│       ├── __init__.py
│       └── urls.py      # URL endpoints
├── tests/
│   └── __init__.py
├── requirements.txt
├── .env.example
├── .env
├── .gitignore
└── README.md
```
