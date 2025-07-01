FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Make the script executable
RUN chmod +x entrypoint.sh


# Expose port
EXPOSE 5000

# Set environment variable for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Use the entrypoint to initialize DB and run Flask
ENTRYPOINT ["./entrypoint.sh"]

