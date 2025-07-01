#!/bin/sh

# Initialize DB if not already present
if [ ! -f database.db ]; then
  echo "Initializing database..."
  python database.py
fi

# Start Flask app
flask run --host=0.0.0.0