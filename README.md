VoxCart is a full-stack, production-representative AI e-commerce chatbot built specifically as a controlled research target for systematic LLM vulnerability assessment. This repository contains the pre-hardening version. The complete methodology, scan results, and hardening architecture are documented in the published case study.

Contact: shri.pachpor24@gmail.com

## Security Research

This repository is the pre-hardening version of VoxCart, published to document real LLM vulnerability findings. Results from Garak and Giskard before hardening:

- DAN jailbreak resistance: 0% (full safety bypass on every tested attempt)
- Harmful content injection resistance: 10.6%
- Spam and phishing detection: 17.3%
- XSS-style data exfiltration resistance: 50%

After implementing a four-layer hardening architecture (LLM-Guard input scanning, semantic defence pipeline, LLM-Guard output scanning, session-level rate limiting), all probes reached 100% resistance and ethical issues reduced by 33%.

The hardening implementation is not in this repository. It is private IP. The pre-hardening codebase is published so any engineer with Garak installed can independently reproduce the baseline findings and verify the research is not fabricated.

Full methodology and findings: shri.pachpor24@gmail.com

## Technology Stack

**AI / LLM**
- OpenAI GPT-3.5-turbo + LangChain: conversational intelligence and orchestration

**Vector Search (RAG)**
- FAISS + ChromaDB: semantic product search

**Backend**
- FastAPI (Python) + SQLAlchemy ORM: REST endpoints, business logic, data access

**Database**
- PostgreSQL + Alembic migrations

**Authentication**
- JWT tokens + bcrypt password hashing

**Frontend**
- React + TypeScript + Tailwind CSS + Vite

## Architecture
├── app/                    # Main FastAPI application
│   ├── api/               # API endpoints
│   ├── core/              # Database, security, logging
│   ├── models/            # SQLAlchemy and Pydantic models
│   ├── services/          # Business logic (chat, ecommerce, payments)
│   └── main.py            # Application entry point
├── frontend/              # React TypeScript application
├── alembic/               # Database migrations
└── tests/                 # Test suite

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL database
- OpenAI API key

### Backend Setup

1. Clone and navigate to the project:
git clone https://github.com/shrikantpachpor/voxcart-ai-chatbot.git
cd voxcart-ai-chatbot

2. Create and activate virtual environment:
python -m venv .venv
..venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate     # Linux/Mac

3. Install dependencies:
pip install .

4. Configure environment variables:
cp .env.template .env

5. Run database migrations:
alembic upgrade head

6. Start the backend server:
uvicorn app.main:app --reload

### Frontend Setup

1. Navigate to frontend directory and install dependencies:
cd frontend
npm install

2. Start the development server:
npm start

## Environment Variables

- `OPENAI_API_KEY` - OpenAI API key
- `SESSION_SECRET_KEY` - Secret key for session middleware
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` - PostgreSQL connection
- `ALLOWED_ORIGINS` - CORS origins

See `.env.template` for the complete list.

## License

MIT License. See LICENSE file for details.

---

Research and development by [Shrikant Pachpor](https://linkedin.com/in/shrikantpachpor)
