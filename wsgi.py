#!/usr/bin/env python3
"""WSGI entry point for production deployment."""

import os

from app import create_app

# Create application instance
application = create_app()

if __name__ == "__main__":
    # Production server configuration
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5001))

    application.run(host=host, port=port)
