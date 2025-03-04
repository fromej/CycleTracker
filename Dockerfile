FROM python:3.12-slim

WORKDIR /app

# Copy application files
COPY . /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install uv && uv pip install --system --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose the application port
EXPOSE 8000

# Ensure the database directory exists
RUN mkdir -p /app/app/data

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]