import os
import sys

# Add the application directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from run import application

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))