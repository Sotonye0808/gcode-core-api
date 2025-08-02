# GCode Core API - Setup Instructions

This guide provides step-by-step instructions for setting up and running the GCode Core API service.

## Prerequisites

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.8 or higher
- **pip**: Python package installer (usually included with Python)
- **Memory**: ~120MB when running (fits within PythonAnywhere free tier)

### Verify Prerequisites

```bash
# Check Python version
python --version

# Check pip version
pip --version
```

## Installation Steps

### Step 1: Navigate to Project Directory

```bash
cd gcode-core-api
```

### Step 2: Create Virtual Environment

Creating a virtual environment isolates the project dependencies:

#### Windows:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

#### macOS/Linux:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

Expected packages installed:

- Django==4.2.7
- djangorestframework==3.14.0
- django-cors-headers==4.3.1
- python-dotenv==1.0.0

### Step 4: Environment Configuration

Create a `.env` file in the root directory by copying from the example:

#### Windows:

```bash
copy .env.example .env
```

#### macOS/Linux:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Django Settings
SECRET_KEY=your-unique-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS Settings (for frontend integration)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Frontend Signing Key (for HMAC verification)
FRONTEND_SIGNING_KEY=your-secure-signing-key-here

# Trusted Frontend Origins (for signed requests)
TRUSTED_FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:4200,http://127.0.0.1:4200

# Evaluation API URL (for future integration)
EVALUATION_API_URL=http://localhost:8001/api/
```

### Step 5: Database Setup

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations to create database tables
python manage.py migrate
```

### Step 6: Create Admin User (Optional)

Create a superuser to access the Django admin interface:

```bash
python manage.py createsuperuser
```

Follow the prompts to set:

- Username
- Email address
- Password

## Quick Start Scripts

### Development Server Startup

#### Windows (start_core_server.bat):

```batch
@echo off
echo Starting GCode Core API...
echo.

if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file with your configuration before running again.
    pause
    exit /b 1
)

echo Running database migrations...
python manage.py migrate

echo.
echo Starting Django development server...
echo Core API will be available at http://localhost:8000/api/
echo Admin interface available at http://localhost:8000/admin/
echo.
python manage.py runserver 8000
```

#### macOS/Linux (start_core_server.sh):

```bash
#!/bin/bash
echo "Starting GCode Core API..."
echo

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your configuration before running again."
    exit 1
fi

echo "Running database migrations..."
python manage.py migrate

mkdir -p logs

echo
echo "Starting Django development server..."
echo "Core API will be available at http://localhost:8000/api/"
echo "Admin interface available at http://localhost:8000/admin/"
echo
python manage.py runserver 8000
```

### Make the script executable (macOS/Linux):

```bash
chmod +x start_core_server.sh
```

## API Usage Examples

### Health Check

Test that the API is running:

```bash
curl http://localhost:8000/api/health/
```

Expected response:

```json
{
  "status": "healthy",
  "service": "GCode Core API",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00Z",
  "endpoints": {
    "convert": "/api/convert/",
    "signed_submit": "/api/signed/submit/",
    "signed_retrieve": "/api/signed/retrieve/"
  }
}
```

### SVG to G-code Conversion

Convert SVG data to G-code:

```bash
curl -X POST http://localhost:8000/api/convert/ \
  -H "Content-Type: application/json" \
  -d '{
    "svg_data": "<svg width=\"100\" height=\"100\" xmlns=\"http://www.w3.org/2000/svg\"><rect x=\"10\" y=\"10\" width=\"80\" height=\"80\" fill=\"none\" stroke=\"black\"/></svg>"
  }'
```

### Testing with File Upload

```bash
curl -X POST http://localhost:8000/api/convert/ \
  -F "svg_file=@path/to/your/file.svg"
```

### Admin Interface

Access the Django admin interface at:

```
http://localhost:8000/admin/
```

Use the superuser credentials created in Step 6.

## Troubleshooting

### Common Issues

#### 1. Virtual Environment Not Activating

**Windows:**

```bash
# Try using the full path
C:\path\to\your\project\venv\Scripts\activate
```

**macOS/Linux:**

```bash
# Ensure you're in the correct directory
pwd
source ./venv/bin/activate
```

#### 2. Dependencies Installation Fails

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try installing with verbose output
pip install -r requirements.txt -v
```

#### 3. Database Migration Errors

```bash
# Reset migrations (development only)
rm -rf core_api/migrations/
python manage.py makemigrations core_api
python manage.py migrate
```

#### 4. Port Already in Use

If port 8000 is already in use:

```bash
# Use a different port
python manage.py runserver 8001
```

#### 5. CORS Errors

Update your `.env` file to include your frontend URL:

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:4200,http://yourdomain.com
```

### Checking Logs

If you encounter issues, check the application logs:

```bash
# View recent logs (after creating logs directory)
tail -f logs/django.log  # macOS/Linux
type logs\django.log     # Windows

# Check Django server output in the terminal where you ran runserver
```

### Environment Variables Issues

Verify your `.env` file is in the correct location and properly formatted:

```bash
# Check if .env file exists
ls -la .env  # macOS/Linux
dir .env     # Windows

# Verify environment variables are loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('SECRET_KEY'))"
```

## Testing the Installation

### Run the Test Suite

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test core_api

# Run with verbose output
python manage.py test --verbosity=2
```

### Test Coverage (Optional)

```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
```

## Development Setup

### Code Style and Linting (Optional)

```bash
# Install development tools
pip install black flake8 isort

# Format code
black .

# Check code style
flake8 .

# Sort imports
isort .
```

### Git Setup (Optional)

```bash
# Initialize git repository
git init

# Add gitignore
echo "venv/
*.pyc
__pycache__/
.env
db.sqlite3
logs/
.coverage
htmlcov/" > .gitignore

# Add and commit initial code
git add .
git commit -m "Initial Core API setup"
```

## Production Deployment Notes

### Environment Variables for Production

```env
SECRET_KEY=generate-a-long-random-secret-key-for-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourfrontend.com
FRONTEND_SIGNING_KEY=secure-production-signing-key
TRUSTED_FRONTEND_ORIGINS=https://yourfrontend.com
```

### PythonAnywhere Specific Setup

1. **Upload files** to your PythonAnywhere account
2. **Create virtual environment** in the files section
3. **Install dependencies** via console
4. **Configure WSGI file** to point to your Django application
5. **Set environment variables** in the web app configuration
6. **Configure static files** serving

### Security Checklist

- [ ] Change SECRET_KEY to a secure value
- [ ] Set DEBUG=False in production
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Use HTTPS in production
- [ ] Set secure CORS origins
- [ ] Use strong FRONTEND_SIGNING_KEY
- [ ] Configure proper database (PostgreSQL/MySQL for production)

## Next Steps

1. **Configure Frontend Integration**: Update frontend to use the Core API endpoints
2. **Set up Evaluation API**: Configure the companion evaluation service
3. **Test Integration**: Verify frontend can communicate with both APIs
4. **Deploy to Production**: Set up production environment on PythonAnywhere

## Getting Help

1. **Check the API Documentation:** See `API_DOCUMENTATION.md` for detailed endpoint documentation
2. **Run the test script:** Execute the test suite to verify functionality
3. **Check Django admin:** Create a superuser and access admin at `http://localhost:8000/admin/`
4. **Review logs:** Check the Django logs for error messages

For additional support:

**Author**: Sotonye Dagogo  
**Email**: sotydagz@gmail.com  
**GitHub**: [@Sotonye0808](https://github.com/Sotonye0808)
