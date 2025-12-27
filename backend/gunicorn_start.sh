#!/bin/bash
# Start Gunicorn for Flask backend
source venv/bin/activate
exec gunicorn -b 0.0.0.0:8080 app:app
