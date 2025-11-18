# Running the Django Blog Project Locally

This guide provides instructions to run the TechMust Blog Django application on your local machine.

## Prerequisites

- Python 3.8+ (Note: Python 3.13 has issues with mysqlclient, so we use SQLite for local development)
- Git

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/JustNDung/blog-page-app-django-on-aws.git
cd blog-page-app-django-on-aws-1
```

### 2. Install Dependencies

Navigate to the src directory and install Python packages:

```bash
cd src
pip install -r ../requirements.txt
```

Note: mysqlclient may fail to install on Python 3.13. This is okay as we'll use SQLite for local development.

### 3. Configure Environment

The project uses python-decouple for configuration. A `.env` file is already present in `src/` with:

```
SECRET_KEY=i2^$(%im!!)@lwenn9nk40%yo#ay-lqs_#3p=v(^7-1-%ck$y@
PASSWORD=TechMust1234
```

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/

## Features Available

- User registration and authentication
- Create, view, update, and delete blog posts
- Upload images to posts
- Like posts
- Comment on posts
- User profiles

## Configuration Changes Made for Local Development

For local development, the following changes were made to `src/cblog/settings.py`:

- `DEBUG = True` (for development)
- Database changed from MySQL to SQLite
- Static files configured for local serving instead of S3
- AWS S3 settings commented out

## Troubleshooting

### CSS Not Loading
- Ensure DEBUG=True in settings.py
- Static files should be served automatically in development mode

### Database Errors
- Run `python manage.py migrate` to apply migrations
- If issues persist, delete `db.sqlite3` and re-run migrations

### Port Already in Use
- Use `python manage.py runserver 8001` to run on a different port

## Production Deployment

For production deployment on AWS (as originally intended):

- Set `DEBUG = False`
- Configure MySQL database
- Set up AWS S3 for static files and media
- Configure proper security settings

Refer to the main README.md for AWS deployment instructions.
