"""
Referee Assignment System
A Flask web application for managing referee assignments to football matches.
"""

import os
from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    print(" Starting Referee Assignment System...")
    print(f"📍 Running on http://localhost:{port}")
    print("🔧 Press CTRL+C to quit")

    app.run(host='0.0.0.0', port=port, debug=debug)
