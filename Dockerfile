# Use an official Python runtime as the base image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Expose Flask port (Fly.io uses 8080)
EXPOSE 8080

# Create a startup script to ensure Ollama starts first
RUN echo -e "#!/bin/bash\nollama serve & sleep 5\nexec gunicorn -b 0.0.0.0:8080 app:app" > /app/start.sh
RUN chmod +x /app/start.sh

# Start Ollama, then Flask
CMD ["/app/start.sh"]
