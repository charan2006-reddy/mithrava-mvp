<div align="center">

# 🌾 Mithrava

**AI-Powered Agricultural Assistant for Indian Farmers**

*Empowering every farmer with intelligent crop management, real-time market insights, and expert guidance — in their own language.*

---

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-24-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?style=for-the-badge&logo=openai&logoColor=white)

</div>

---

## ✨ Features

- **🗣️ Multilingual AI Chat (Mitra)** — Talk to your personal farming assistant in Telugu, Kannada, Hindi, Marathi, and more
- **📡 Real-Time Weather Alerts** — Hyper-local weather data with crop-specific advisories
- **📊 Market Price Tracking** — Live mandi prices across India with trend analysis
- **🌿 Crop Health Monitoring** — AI-powered disease detection from photos
- **💧 Irrigation Management** — Smart scheduling based on soil, weather, and crop needs
- **🗣️ Voice Input** — Speak in your language, get answers instantly
- **👥 Community Forum** — Connect with fellow farmers, share knowledge
- **📞 Expert Consultations** — Schedule video calls with agricultural experts
- **🏪 Vendor Marketplace** — Find trusted seed, fertilizer, and tool suppliers
- **📊 Farm Dashboard** — Track all your lands, crops, and finances in one place

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      Nginx (Port 80)                     │
│              Reverse Proxy + Rate Limiting                │
├─────────────────────┬────────────────────────────────────┤
│                     │                                    │
│   /api/*            │           /*                       │
│                     │                                    │
│   ┌─────────────┐   │   ┌──────────────────────────┐    │
│   │   Backend   │   │   │        Frontend          │    │
│   │  FastAPI    │   │   │       Next.js 14         │    │
│   │  Port 8000  │   │   │       Port 3000          │    │
│   └──────┬──────┘   │   └──────────────────────────┘    │
│          │          │                                    │
│   ┌──────┴──────┐   │                                    │
│   │  PostgreSQL  │   │                                    │
│   │  + pgvector  │   │                                    │
│   │  Port 5432  │   │                                    │
│   └─────────────┘   │                                    │
│   ┌─────────────┐   │                                    │
│   │    Redis     │   │                                    │
│   │  Port 6379  │   │                                    │
│   └─────────────┘   │                                    │
└─────────────────────┴────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) >= 24.0
- [Docker Compose](https://docs.docker.com/compose/install/) >= 2.20

### One-Command Setup

**Windows:**
```cmd
scripts\setup.bat
```

**Linux / macOS:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Manual Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/mithrava.git
cd mithrava

# 2. Start all services
docker-compose up -d

# 3. Wait for services to be healthy (check with)
docker-compose ps

# 4. Seed the database with sample data
docker-compose exec backend python scripts/seed_db.py

# 5. Open in browser
open http://localhost:3000
```

The API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs).

## 🛠️ Development Setup

### Backend Development

```bash
# Start only infrastructure (postgres + redis)
docker-compose up -d postgres redis

# Set up Python virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run the backend with hot-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Run the development server
npm run dev
```

### Full Stack with Docker (Development Mode)

```bash
# Uses docker-compose.dev.yml overrides with hot-reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

## 📁 Project Structure

```
mithrava/
├── backend/
│   ├── app/
│   │   ├── api/            # API route handlers
│   │   ├── core/           # Config, security, dependencies
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── agents/         # AI agent logic (Mitra)
│   │   └── main.py         # FastAPI application
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js App Router pages
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Utilities and API clients
│   │   ├── stores/         # State management
│   │   └── types/          # TypeScript type definitions
│   ├── public/
│   ├── package.json
│   └── next.config.js
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── init.sql
│   └── nginx.conf
├── scripts/
│   ├── seed_db.py
│   ├── setup.bat
│   └── setup.sh
├── docker-compose.yml
├── docker-compose.dev.yml
├── .gitignore
└── README.md
```

## 🔧 Environment Variables

### Backend (`.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://mithrava:mithrava@localhost:5432/mithrava` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT signing key | (generate a strong random key) |
| `OPENAI_API_KEY` | OpenAI API key for Mitra AI | (required) |
| `WHATSAPP_TOKEN` | WhatsApp Business API token | (optional) |
| `ENVIRONMENT` | `development` or `production` | `development` |

### Frontend (`.env.local`)

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000/api/v1` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | `ws://localhost:8000/ws` |

## 📚 API Documentation

Once the backend is running, access the auto-generated API docs:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest -v
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test
npm run test:e2e
```

## 🤝 Contributing

We welcome contributions from the community! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'feat: add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `style:` — Code style changes (formatting, etc.)
- `refactor:` — Code refactoring
- `test:` — Adding or updating tests
- `chore:` — Maintenance tasks

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for the farmers of India**

*When technology meets the soil, crops grow taller.*

</div>
