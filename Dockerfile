# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables to force headless mode
ENV OPENCV_HEADLESS=1
ENV DISPLAY=""

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for uploads and database
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]