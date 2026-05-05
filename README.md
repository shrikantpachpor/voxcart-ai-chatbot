# VoxCart - AI E-commerce Chatbot Platform
Production-grade AI e-commerce chatbot built as a controlled security 
research target. GPT-3.5-turbo + LangChain + FastAPI + PostgreSQL + React. 
Used as the research target for systematic LLM vulnerability assessment 
using Garak and Giskard. This repository contains the pre-hardening version.

## 🌟 Features

- **AI-Powered Conversations**: GPT-3.5-turbo with LangChain for intelligent chat responses
- **E-commerce Functions**: Product search, cart management, checkout, order tracking
- **Vector Search**: ChromaDB and FAISS for semantic product search
- **User Authentication**: JWT-based auth with secure password hashing
- **Payment Processing**: Integrated payment service with card tokenization
- **Modern Frontend**: React with TypeScript, Tailwind CSS
- **RESTful API**: FastAPI with automatic OpenAPI documentation

## 🏗️ Architecture

```
├── app/                    # Main FastAPI application
│   ├── api/               # API endpoints
│   ├── core/              # Database, security, logging
│   ├── models/            # SQLAlchemy and Pydantic models
│   ├── services/          # Business logic (chat, ecommerce, payments)
│   └── main.py            # Application entry point
├── frontend/              # React TypeScript application
├── alembic/               # Database migrations
└── tests/                 # Test suite
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL database
- OpenAI API key

### Backend Setup

1. Clone and navigate to the project:

```powershell
git clone https://github.com/shrikantpachpor/voxcart-ai-chatbot.git
cd voxcart
```

2. Create and activate virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# or: source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:

```powershell
pip install .
# or with Poetry: poetry install
```

4. Configure environment variables:

```powershell
cp .env.template .env
# Edit .env and add your values:
# - OPENAI_API_KEY
# - SESSION_SECRET_KEY
# - DB_USER, DB_PASSWORD, DB_HOST, DB_NAME
```

5. Run database migrations:

```powershell
alembic upgrade head
```

6. Start the backend server:

```powershell
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to frontend directory:

```powershell
cd frontend
```

2. Install dependencies:

```powershell
npm install
```

3. Configure environment:

```powershell
cp .env.example .env
# Update API endpoint if needed
```

4. Start the development server:

```powershell
npm start
```

The frontend will be available at `http://localhost:3000`

## 🔑 Environment Variables

### Backend (.env)

- `OPENAI_API_KEY` - OpenAI API key for chat and embeddings
- `SESSION_SECRET_KEY` - Secret key for session middleware
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` - PostgreSQL connection
- `ALLOWED_ORIGINS` - CORS origins (default: `http://localhost:3000`)
- `LOG_LEVEL` - Logging level (INFO, DEBUG, etc.)

See [.env.template](.env.template) for a complete list.

## 📚 Documentation

- **Architecture Guide**: See [.github/copilot-instructions.md](.github/copilot-instructions.md)
- **API Documentation**: Available at `/docs` when running the server
- **Frontend README**: [frontend/README.md](frontend/README.md)
- **GitHub Readiness**: [app/GITHUB_READY_CHECKLIST.md](app/GITHUB_READY_CHECKLIST.md)

## 🧪 Testing

```powershell
# Run backend tests
pytest

# Run frontend tests
cd frontend
npm test
```

## 🛠️ Development

### Database Migrations

```powershell
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Code Quality

```powershell
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 📦 Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - SQL toolkit and ORM
- PostgreSQL - Database
- Alembic - Database migrations
- OpenAI - GPT-3.5-turbo for AI chat
- LangChain - LLM orchestration
- ChromaDB - Vector database
- Passlib - Password hashing

**Frontend:**
- React - UI library
- TypeScript - Type-safe JavaScript
- Tailwind CSS - Utility-first CSS
- Vite - Build tool

## 🔒 Security

This project includes security best practices:
- Password hashing with bcrypt
- JWT token authentication
- Environment-based secrets management
- CORS configuration
- Input sanitization

This repository is the research target used in a systematic LLM 
vulnerability assessment. This is the pre-hardening version, 
intentionally representing a default GPT-3.5-turbo deployment 
with no AI-specific security measures applied.

Assessment was conducted using Garak and Giskard against OWASP 
Top 10 for LLM Applications vulnerability categories.

Findings before hardening:
- DAN jailbreak resistance: 0%
- Spam and phishing detection: 17%
- Harmful content injection resistance: 10.6%

Full findings, business impact analysis, and remediation methodology 
are documented in the case study. Available on request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Important Notes

- **Never commit** your `.env` file to version control
- Rotate API keys before deploying to production
- Use strong, randomly generated secrets for `SESSION_SECRET_KEY`
- Review the security checklist in [app/GITHUB_READY_CHECKLIST.md](app/GITHUB_READY_CHECKLIST.md)

## 📞 Support

For issues and questions, please open a GitHub issue.

---

Research and development by Shrikant Pachpor 
[linkedin.com/in/shrikantpachpor](https://linkedin.com/in/shrikantpachpor)

