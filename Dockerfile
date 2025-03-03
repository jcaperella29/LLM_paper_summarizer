# Use Python base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Ensure script uses LF (Unix) format and is executable
RUN apt-get update && apt-get install -y dos2unix && dos2unix /app/start.sh && chmod +x /app/start.sh

# Expose Flask port
EXPOSE 8080

# Start Ollama, then Flask
CMD ["/app/start.sh"]
