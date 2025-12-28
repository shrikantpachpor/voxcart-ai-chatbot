# VoxCart - AI E-commerce Chatbot Platform

## Architecture Overview

This is a **full-stack e-commerce chatbot system** with FastAPI backend, React frontend, and AI-powered conversational commerce. The project uses a **dual main.py structure** - one at root (`main.py`) and one in `app/main.py` (the primary application entry point).

### Core Components
- **Backend**: FastAPI with SQLAlchemy, PostgreSQL database, Alembic migrations
- **Frontend**: React with Create React App (port 3000), Tailwind CSS
- **AI Engine**: OpenAI GPT-3.5-turbo with LangChain for conversation management
- **Vector DB**: ChromaDB for product search, FAISS for embeddings
- **Authentication**: JWT tokens with OAuth2PasswordBearer
- **Payment**: Custom payment service with card tokenization

## Key Architectural Patterns

### 1. Intent-Based Conversation Routing
The chatbot uses a **dynamic intent handler system** in `app/services/chat_service.py`:
- `IntentRouter` class routes intents to specialized handlers
- Each handler (`ProductSearchHandler`, `AddToCartHandler`, etc.) implements `IntentHandler` interface
- Conversation state persists in `STATE_STORE` in-memory dictionary
- Use `ConversationState` model for session management

### 2. Service Layer Architecture
Services are in `app/services/` and handle business logic:
- `chat_service.py`: Main conversation orchestration
- `ecommerce_service.py`: Product search, cart management, checkout
- `payment_service.py`: Payment processing and method storage
- `profile_service.py`: User profile and preference management
- `order_service.py`: Order tracking and shipment details

### 3. Database Models Structure
Located in `app/models/database_models.py`:
- Uses **string references** for relationships to avoid circular imports
- `User` model has relationships to `PaymentMethod`, `Transaction`, `UserProfile`, `OrderHistory`
- JSON columns for flexible data (`preferences`, `search_history`, `tracking_numbers`)
- Validators using `@validates` decorator for JSON field validation

## Development Workflows

### Environment Setup
```bash
# Poetry is the package manager (pyproject.toml)
poetry install
poetry shell

# Frontend setup
cd frontend && npm install && npm start

# Database migrations
alembic upgrade head
```

### Running the Application
```bash
# Backend (from root directory)
uvicorn app.main:app --reload --port 8000

# Frontend 
cd frontend && npm start  # Runs on localhost:3000
```

### Database Operations
- **Migrations**: Use Alembic - `alembic revision --autogenerate -m "message"`
- **Database URL**: Configure in `alembic/env.py` and environment variables
- **Session Management**: Use `SessionLocal()` from `app.core.database`

## Critical Code Patterns

### 1. Conversation State Management
```python
# Always get/save state for chat sessions
state = self._get_state(session_id)
# ... modify state ...
self._save_state(session_id, state)
```

### 2. Database Session Handling
```python
db = SessionLocal()
try:
    # database operations
    db.commit()
finally:
    db.close()
```

### 3. Intent Handler Pattern
```python
class MyHandler(IntentHandler):
    def handle(self, analysis, state, session_id, current_user):
        # Handler logic here
        return response_string
```

### 4. API Endpoint Pattern
All endpoints in `app/api/endpoints/` use:
- Pydantic models for request/response validation
- `Depends(get_current_user)` for authentication
- Consistent error handling with HTTPException

## Security & Authentication

- **JWT Tokens**: Created with `create_access_token()` from `app.core.security`
- **Password Hashing**: Uses `passlib[bcrypt]` 
- **Rate Limiting**: `rate_limit_check()` function (currently commented out)
- **Input Sanitization**: `sanitize_input()` from `app.utils.sanitization`

## Frontend Integration

- **CORS**: Configured for `http://localhost:3000` in `app/main.py`
- **Session Management**: Uses `SessionMiddleware` with cookies
- **API Calls**: Frontend expects specific response formats with popup triggers (`[[SHOW_CART]]`, `[[SHOW_PROFILE]]`)

## Testing & Development

### Test Structure
- Tests in `app/tests/` directory
- Current test file: `app/tests/test_db.py` 
- Use pytest for running tests

### Key Environment Variables
Configure in `.env`:
- `OPENAI_API_KEY`: For GPT integration
- `SESSION_SECRET_KEY`: For session middleware
- Database connection string for Alembic

### Debugging Chat Issues
1. Check conversation state in `STATE_STORE`
2. Review intent analysis in chat logs
3. Verify database session handling in services
4. Test with specific intent phrases to trigger handlers

## Common Gotchas

1. **Dual main.py**: Use `app/main.py` for development, root `main.py` is simpler version
2. **JSON Columns**: PostgreSQL JSONB vs JSON - use JSONB for `tracking_numbers`, `geolocation_history`
3. **Memory State**: `STATE_STORE` is in-memory - will reset on server restart
4. **Relationship Loading**: Use `joinedload()` for efficient relationship queries
5. **Frontend Paths**: React app expects backend on port 8000, frontend on 3000

## Quick File Reference

- **Main Entry**: `app/main.py`
- **Chat Logic**: `app/services/chat_service.py` 
- **Database Models**: `app/models/database_models.py`
- **API Routes**: `app/api/endpoints/chat.py`
- **Configuration**: `pyproject.toml`, `alembic.ini`
- **Frontend**: `frontend/src/` (React components)

When making changes, always consider the conversation state management, database session handling, and intent routing system. The architecture prioritizes modularity and extensibility for adding new commerce features.