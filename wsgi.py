
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
