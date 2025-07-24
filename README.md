<div align="center">
  <h1>🌟 SnapVerse API</h1>
  <p><strong>A Comprehensive Social Media Backend Platform</strong></p>
  
  [![Django](https://img.shields.io/badge/Django-5.2.4-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com/)
  [![DRF](https://img.shields.io/badge/DRF-3.16.0-ff1709?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
  [![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
</div>

---

## 🎯 Overview

**SnapVerse** is a production-ready RESTful social media API built with Django REST Framework. It provides comprehensive backend functionality for modern social media platforms with enterprise-grade security and scalability.

### ✨ Key Features

- **🔐 JWT Authentication** with Djoser integration
- **👤 User Management** with custom profiles and privacy controls
- **📱 Posts & Comments** with nested threading and reactions
- **🤝 Follow System** with approval workflow for private accounts
- **🎨 Media Handling** with image validation and optimization
- **📚 API Documentation** with Swagger/ReDoc integration
- **🔒 Security** with rate limiting and permission controls
- **📊 Admin Panel** with comprehensive management tools

## 🛠 Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Framework** | Django | 5.2.4 |
| **API** | Django REST Framework | 3.16.0 |
| **Authentication** | Djoser + Simple JWT | 2.3.3 + 5.5.1 |
| **Documentation** | drf-yasg | 1.21.10 |
| **Database** | PostgreSQL/SQLite | - |
| **Media** | Pillow | 11.3.0 |
| **Caching** | Redis | - |

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/nazmulh24/SnapVerse_API.git
cd SnapVerse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/users_data.json
python manage.py loaddata fixtures/posts_data.json
python manage.py loaddata fixtures/follows_data.json

# Run server
python manage.py runserver
```

### Access Points
- **API Root**: `http://127.0.0.1:8000/api/v1/`
- **Swagger Docs**: `http://127.0.0.1:8000/swagger/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`

## 📚 API Documentation

### Authentication
All protected endpoints require JWT token in header:
```http
Authorization: JWT your_access_token_here
```

### Core Endpoints

**Authentication:**
```
POST /api/v1/auth/users/                 # Register
POST /api/v1/auth/jwt/create/            # Login
POST /api/v1/auth/jwt/refresh/           # Refresh token
POST /api/v1/auth/users/reset_password/  # Password reset
```

**Users:**
```
GET    /api/v1/users/                    # List users
GET    /api/v1/users/{username}/         # User profile
GET    /api/v1/users/{username}/posts/   # User posts
PUT    /api/v1/users/me/                 # Update profile
```

**Posts:**
```
GET    /api/v1/posts/                    # Feed
POST   /api/v1/posts/                    # Create post
GET    /api/v1/posts/{id}/               # Get post
PUT    /api/v1/posts/{id}/               # Update post
DELETE /api/v1/posts/{id}/               # Delete post
POST   /api/v1/posts/{id}/like/          # Like/unlike
```

**Comments:**
```
GET    /api/v1/posts/{id}/comments/      # Get comments
POST   /api/v1/posts/{id}/comments/      # Create comment
PUT    /api/v1/comments/{id}/            # Update comment
DELETE /api/v1/comments/{id}/            # Delete comment
```

**Follows:**
```
GET    /api/v1/follows/                  # List relationships
POST   /api/v1/follows/                  # Follow user
DELETE /api/v1/follows/{id}/             # Unfollow
POST   /api/v1/follows/{id}/approve/     # Approve request
```

### Example Usage

**User Registration:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepass123",
    "re_password": "securepass123"
  }'
```

**Create Post:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts/ \
  -H "Authorization: JWT your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "caption": "Beautiful sunset! 🌅",
    "privacy": "public"
  }'
```

## ⚙️ Configuration

### Environment Variables
Create `.env` file:

```ini
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_USE_TLS=True
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Database (Production)
DATABASE_URL=postgresql://user:password@localhost:5432/snapverse

# Security
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Optional: Cloud Storage
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Docker Setup

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/snapverse
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: snapverse
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password

  redis:
    image: redis:7-alpine
```

## 🏗️ Project Architecture

```
SnapVerse/
├── api/                    # Core API configuration
│   ├── models.py          # Shared models
│   ├── urls.py            # API routing
│   ├── permissions.py     # Custom permissions
│   └── validators.py      # File validators
├── users/                 # User management
│   ├── models.py         # Custom User model
│   ├── views.py          # User endpoints
│   └── serializers.py    # User serializers
├── posts/                # Posts & comments
│   ├── models.py         # Post/Comment models
│   ├── views.py          # Post endpoints
│   └── serializers.py    # Post serializers
├── relationships/        # Follow system
│   ├── models.py         # Follow model
│   ├── views.py          # Follow endpoints
│   └── serializers.py    # Follow serializers
├── fixtures/             # Sample data
├── media/                # Uploaded files
└── snap_verse/           # Django settings
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report

# Run specific tests
python manage.py test users
python manage.py test posts.tests.PostAPITest
```

## 🚀 Deployment

### Production Setup

```bash
# Install production dependencies
pip install gunicorn psycopg2-binary

# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn snap_verse.wsgi:application --bind 0.0.0.0:8000
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 🔒 Security Features

- **JWT Authentication** with token refresh
- **Rate Limiting** (100/hour for anonymous, 1000/hour for users)
- **Input Validation** and sanitization
- **File Upload Security** with size/format validation
- **CORS Protection** for cross-origin requests
- **Privacy Controls** (public, private, followers-only)
- **Permission System** with object-level permissions

## ⚡ Performance

- **Database Optimization** with select_related/prefetch_related
- **Redis Caching** for frequently accessed data
- **Image Optimization** with automatic compression
- **Pagination** for all list endpoints
- **Efficient Queries** with proper indexing

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Create Pull Request

### Development Setup
```bash
# Install dev dependencies
pip install black flake8 pre-commit

# Set up pre-commit hooks
pre-commit install

# Run code formatting
black .
flake8
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📚 **Documentation**: Check README and Swagger docs
- 🐛 **Issues**: [GitHub Issues](https://github.com/nazmulh24/SnapVerse_API/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/nazmulh24/SnapVerse_API/discussions)
- 📧 **Email**: [snazmulhossains24@gmail.com](mailto:snazmulhossains24@gmail.com)

## 👨‍💻 Author

**Nazmul Hossain**
- GitHub: [@nazmulh24](https://github.com/nazmulh24)
- Email: snazmulhossains24@gmail.com

---

<div align="center">

### 🌟 **Thank you for checking out SnapVerse!**

**If you found this project helpful, please ⭐ star the repository!**

*Built with ❤️ using Django REST Framework*

</div>
