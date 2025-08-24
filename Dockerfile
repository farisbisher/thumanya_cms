FROM python:3.11-slim

WORKDIR /cms_system

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project code
COPY . .

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "cms_system/manage.py", "runserver", "0.0.0.0:8000"]