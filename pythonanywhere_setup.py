#!/usr/bin/env python3
"""
PythonAnywhere Setup Script for CRM Rabbani
This script helps prepare your Django project for PythonAnywhere deployment
"""

import os
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def create_pythonanywhere_settings():
    """Create PythonAnywhere-specific settings"""
    settings_content = '''
"""
PythonAnywhere settings for CRM Rabbani
"""

from .settings import *
import os

# PythonAnywhere specific settings
DEBUG = False

# Allow PythonAnywhere domains
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com', 'localhost', '127.0.0.1']

# Database configuration for PythonAnywhere
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yourusername$crm_rabbani',
        'USER': 'yourusername',
        'PASSWORD': 'your-database-password',
        'HOST': 'yourusername.mysql.pythonanywhere-services.com',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Static files configuration
STATIC_ROOT = '/home/yourusername/mysite/static/'
STATIC_URL = '/static/'

# Media files configuration
MEDIA_ROOT = '/home/yourusername/mysite/media/'
MEDIA_URL = '/media/'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/home/yourusername/mysite/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
'''
    
    with open('rabbani/pythonanywhere_settings.py', 'w') as f:
        f.write(settings_content)
    
    print("✅ Created pythonanywhere_settings.py")

def create_virtualenv_requirements():
    """Create requirements.txt for PythonAnywhere"""
    requirements = '''Django==5.2.5
crispy-bootstrap5==0.7
django-crispy-forms==2.2
django-filter==24.3
openpyxl==3.1.5
Pillow==10.4.0
mysqlclient==2.2.4
whitenoise==6.7.0
gunicorn==23.0.0
'''
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Updated requirements.txt for PythonAnywhere")

def create_wsgi_file():
    """Create WSGI configuration file for PythonAnywhere"""
    wsgi_content = '''
import os
import sys

# Add your project directory to the Python path
path = '/home/yourusername/mysite'
if path not in sys.path:
    sys.path.append(path)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rabbani.pythonanywhere_settings')

# Configure Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
'''
    
    with open('wsgi.py', 'w') as f:
        f.write(wsgi_content)
    
    print("✅ Created wsgi.py for PythonAnywhere")

def main():
    """Main setup function"""
    print("🚀 PythonAnywhere Setup for CRM Rabbani")
    print("=" * 50)
    
    # Create PythonAnywhere settings
    create_pythonanywhere_settings()
    
    # Update requirements
    create_virtualenv_requirements()
    
    # Create WSGI file
    create_wsgi_file()
    
    print("\n✅ Setup completed!")
    print("\n📋 Next Steps:")
    print("1. Sign up at https://www.pythonanywhere.com/")
    print("2. Follow the deployment guide in README_PYTHONANYWHERE.md")
    print("3. Replace 'yourusername' with your actual PythonAnywhere username")

if __name__ == "__main__":
    main()
