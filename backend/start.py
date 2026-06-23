import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Change to backend directory
os.chdir(backend_dir)

# Import and run uvicorn
from uvicorn import run
run('app.main:app', host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
