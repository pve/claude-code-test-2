#!/usr/bin/env python3
"""Development server entry point."""

import os
from app import create_app

if __name__ == '__main__':
    app = create_app()
    
    # Development server configuration
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host=host, port=port, debug=debug)