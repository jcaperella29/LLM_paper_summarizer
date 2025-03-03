# Use Python base image (forcing x86_64 if needed)
FROM --platform=linux/amd64 python:3.10

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y dos2unix

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Ensure script is executable inside container
RUN dos2unix /app/start.sh && chmod +x /app/start.sh

# Expose Flask port
EXPOSE 8080

# Start Ollama, then Flask
CMD ["/bin/bash", "/app/start.sh"]
