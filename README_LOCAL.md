# SentimentStream - Local Development Setup

This guide will help you set up and run SentimentStream locally with all APIs configured inline.

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys** (Optional)
   Edit `config.py` and replace the placeholder API keys with your actual keys:
   - `GEMINI_API_KEY`: For AI image generation
   - `STRIPE_SECRET_KEY` & `STRIPE_PUBLISHABLE_KEY`: For payment processing

3. **Run the Application**
   ```bash
   python run_local.py
   ```

4. **Access the Application**
   Open your browser and go to: http://localhost:5000

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## 🔧 Detailed Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd SentimentStream
```

### 2. Create Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys (Optional)

The application is configured to work without API keys for basic functionality. However, for full features:

#### Google Gemini API (for AI image generation)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Edit `config.py` and replace `"your-gemini-api-key-here"` with your actual key

#### Stripe API (for payment processing)
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Get your test API keys
3. Edit `config.py` and replace:
   - `"sk_test_your-stripe-secret-key-here"` with your Stripe secret key
   - `"pk_test_your-stripe-publishable-key-here"` with your Stripe publishable key

### 5. Run the Application

#### Option 1: Using the Local Runner (Recommended)
```bash
python run_local.py
```

#### Option 2: Direct Flask Run
```bash
python app.py
```

#### Option 3: Using Flask CLI
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

## 🎯 Features Available

### Without API Keys
- ✅ User registration and login
- ✅ Basic poster templates
- ✅ File upload functionality
- ✅ User profile management
- ✅ Database operations
- ✅ Basic UI/UX

### With API Keys
- ✅ AI-powered poster generation (Gemini)
- ✅ Payment processing (Stripe)
- ✅ Subscription management
- ✅ Watermark-free downloads
- ✅ Advanced features

## 📁 Project Structure

```
SentimentStream/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── run_local.py           # Local development runner
├── models.py              # Database models
├── routes.py              # Application routes
├── gemini_service.py      # AI image generation service
├── stripe_service.py      # Payment processing service
├── image_service.py       # Image processing utilities
├── static/                # Static files (CSS, JS, uploads)
├── templates/             # HTML templates
└── requirements.txt       # Python dependencies
```

## 🔍 Configuration Options

Edit `config.py` to customize:

### Database
```python
DATABASE_URL = "sqlite:///postasy.db"  # SQLite for local development
```

### Upload Settings
```python
UPLOAD_FOLDER = "static/uploads"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
```

### Security
```python
SECRET_KEY = "your-secret-key-change-this-in-production"
WTF_CSRF_ENABLED = False  # Disabled for local development
```

## 🛠️ Development

### Database Management
```bash
# Create database tables
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Reset database
rm postasy.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Logs
Application logs are displayed in the console. For file logging, create a `logs/` directory.

### Debug Mode
The application runs in debug mode by default, which provides:
- Auto-reload on code changes
- Detailed error messages
- Debug toolbar

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt
```

#### 2. Database Errors
```bash
# Reset the database
rm postasy.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

#### 3. Permission Errors
```bash
# Make sure upload directories exist and are writable
mkdir -p static/uploads/posters static/uploads/logos
chmod 755 static/uploads
```

#### 4. Port Already in Use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### API Key Issues

#### Gemini API
- Ensure your API key is valid and has sufficient quota
- Check the Google AI Studio dashboard for usage limits

#### Stripe API
- Use test keys for development
- Ensure webhook endpoints are properly configured for production

## 🔒 Security Notes

### For Local Development
- CSRF protection is disabled for easier testing
- Debug mode is enabled
- Secret keys are set to default values

### For Production
- Set `WTF_CSRF_ENABLED = True`
- Use strong, unique secret keys
- Set `DEBUG = False`
- Use environment variables for sensitive data

## 📚 API Documentation

### Gemini API
- Used for AI-powered poster generation
- Requires valid API key from Google AI Studio
- Handles image generation with retry logic

### Stripe API
- Used for payment processing and subscriptions
- Requires test/live API keys from Stripe Dashboard
- Handles webhooks for subscription updates

## 🚀 Deployment

For production deployment:

1. Set environment variables for sensitive data
2. Use a production database (PostgreSQL recommended)
3. Configure proper logging
4. Set up SSL/TLS certificates
5. Use a production WSGI server (Gunicorn, uWSGI)

## 📞 Support

If you encounter issues:

1. Check the console logs for error messages
2. Verify all dependencies are installed
3. Ensure API keys are correctly configured
4. Check database connectivity
5. Verify file permissions for upload directories

## 🎉 Success!

Once everything is set up, you should see:
```
🎨 SentimentStream - Local Development Server
============================================================
🚀 Setting up local development environment...
✅ Created directory: static/uploads
✅ Created directory: static/uploads/posters
✅ Created directory: static/uploads/logos
✅ Created directory: logs
✅ Environment setup complete!
🔍 Checking dependencies...
✅ flask
✅ flask-sqlalchemy
✅ flask-login
✅ flask-wtf
✅ pillow
✅ google-genai
✅ stripe
✅ werkzeug
✅ jinja2
✅ All dependencies are installed!
🔧 Checking configuration...
✅ Configuration files found!
🎉 All checks passed! Starting the application...
============================================================
🌐 Starting SentimentStream application...
✅ Application loaded successfully!
📍 Server will be available at: http://localhost:5000
🛑 Press Ctrl+C to stop the server
--------------------------------------------------
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

Your SentimentStream application is now running locally! 🎨 