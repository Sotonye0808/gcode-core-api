# GCode Core API

The Core API service handles data persistence, user management, and SVG to G-code conversion for the GCode system. This is the primary service that manages user data and provides signed endpoints for trusted frontend applications.

## Features

### Core Functionality

- **SVG to G-code Conversion**: Convert SVG data to G-code using the py_svg2gcode library
- **User Data Management**: Store and manage user information in SQLite database
- **Signature Data Storage**: Store SVG signatures and generated G-code with metadata
- **Signed Request Handling**: HMAC-verified endpoints for trusted frontend applications

### Database Features

- **User Model**: Store user information (name, email, role, department, faculty)
- **SignatureData Model**: Store SVG data and generated G-code for each user
- **Data Relationships**: One-to-many relationship between users and signatures
- **Admin Interface**: Django admin for managing users and signature data

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Step 1: Navigate to Core API Directory

```bash
cd split-apis/gcode-core-api
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

Create a `.env` file in the core API root directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Frontend Signing Key for HMAC verification
FRONTEND_SIGNING_KEY=your-signing-key-for-hmac-verification

# Trusted Frontend Origins
TRUSTED_FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:4200,http://127.0.0.1:4200

# Evaluation API URL (for future integration)
EVALUATION_API_URL=http://localhost:8001/api/
```

### Step 5: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

## Quick Start

### Start the Development Server

```bash
python manage.py runserver
```

The Core API will be available at `http://localhost:8000/api/`

### Health Check

Test the API is running:

```bash
curl http://localhost:8000/api/health/
```

Expected response:

```json
{
  "status": "healthy",
  "service": "GCode Core API",
  "version": "1.0.0",
  "endpoints": {
    "convert": "/api/convert/",
    "signed_submit": "/api/signed/submit/",
    "signed_retrieve": "/api/signed/retrieve/"
  }
}
```

## API Endpoints

### Open Access Endpoints

These endpoints accept requests from any host without authentication:

| Endpoint    | Method | Description           |
| ----------- | ------ | --------------------- |
| `/convert/` | POST   | Convert SVG to G-code |
| `/health/`  | GET    | API health check      |

### Signed Request Endpoints

These endpoints require HMAC signature verification from trusted origins:

| Endpoint            | Method | Description                                |
| ------------------- | ------ | ------------------------------------------ |
| `/signed/submit/`   | POST   | Submit user data and signature for storage |
| `/signed/retrieve/` | POST   | Retrieve user data by email                |

## Usage Examples

### SVG to G-code Conversion

```bash
curl -X POST http://localhost:8000/api/convert/ \
  -H "Content-Type: application/json" \
  -d '{"svg_data": "<svg width=\"100\" height=\"100\"><rect x=\"10\" y=\"10\" width=\"80\" height=\"80\"/></svg>"}'
```

### Signed Data Submission (requires valid HMAC signature)

```bash
curl -X POST http://localhost:8000/api/signed/submit/ \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "role": "student",
    "svg_data": "<svg>...</svg>",
    "request_signature": "valid_hmac_signature"
  }'
```

## Database Schema

### User Model

```python
{
    "id": "integer (auto-generated primary key)",
    "name": "string (max 255 characters)",
    "email": "string (unique identifier)",
    "role": "choice (student, lecturer, hod, dean, researcher, visitor, other)",
    "department": "string (optional, max 255 characters)",
    "faculty": "string (optional, max 255 characters)",
    "created_at": "datetime (auto-generated)",
    "updated_at": "datetime (auto-updated)",
    "submitted_at": "datetime (set on first submission)"
}
```

### SignatureData Model

```python
{
    "id": "integer (auto-generated primary key)",
    "user": "foreign key to User model",
    "svg_data": "text field (stores SVG content)",
    "gcode_data": "text field (stores generated G-code)",
    "gcode_metadata": "JSON field (stores G-code statistics)",
    "created_at": "datetime (auto-generated)"
}
```

## Configuration

### Environment Variables

| Variable                   | Description                         | Default                      |
| -------------------------- | ----------------------------------- | ---------------------------- |
| `SECRET_KEY`               | Django secret key                   | Required                     |
| `DEBUG`                    | Debug mode                          | `False`                      |
| `ALLOWED_HOSTS`            | Allowed host names                  | `localhost,127.0.0.1`        |
| `CORS_ALLOWED_ORIGINS`     | CORS allowed origins                | `http://localhost:3000`      |
| `FRONTEND_SIGNING_KEY`     | HMAC signing key for frontend       | Required for signed requests |
| `TRUSTED_FRONTEND_ORIGINS` | Trusted origins for signed requests | `http://localhost:3000,...`  |
| `EVALUATION_API_URL`       | URL for evaluation service          | `http://localhost:8001/api/` |

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test core_api

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Deployment

### Production Considerations

1. **Environment Variables**: Set proper production values
2. **Database**: Configure PostgreSQL or MySQL for production
3. **Signing Keys**: Use secure, unique signing keys
4. **CORS Settings**: Restrict to production frontend domains
5. **Static Files**: Configure proper static file serving
6. **HTTPS**: Enable HTTPS for production

### PythonAnywhere Deployment

This service is designed to run within PythonAnywhere's free tier 512MB limit:

- Size: ~100-120MB (lightweight dependencies)
- Dependencies: Django, DRF, CORS headers, python-dotenv
- Database: SQLite (suitable for moderate usage)

## Project Structure

```
gcode-core-api/
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .env                    # Environment variables (create this)
├── gcode_core/             # Django project settings
│   ├── settings.py         # Core API configuration
│   ├── urls.py            # Main URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── core_api/               # Main API application
│   ├── models.py          # Database models
│   ├── serializers.py     # DRF serializers
│   ├── services.py        # Business logic layer
│   ├── views.py           # API views/endpoints
│   ├── urls.py            # API URL patterns
│   ├── admin.py           # Django admin configuration
│   ├── tests.py           # Test cases
│   └── migrations/        # Database migrations
└── py_svg2gcode/          # SVG conversion library
```

## Contributing

1. Follow Django best practices
2. Add comprehensive tests for new features
3. Update documentation for any API changes
4. Ensure database migrations are included
5. Test both open access and signed request functionality

## Contact

**Author**: Sotonye Dagogo  
**Email**: sotydagz@gmail.com  
**GitHub**: [@Sotonye0808](https://github.com/Sotonye0808)
