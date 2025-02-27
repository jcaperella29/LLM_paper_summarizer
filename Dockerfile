# Use an official Python runtime as the base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy all files to the container
COPY . /app

# Install required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Ollama inside the container
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Expose the port that Flask will run on
EXPOSE 8080

# Start Ollama in the background, then run Flask
CMD ollama serve & gunicorn -b 0.0.0.0:8080 app:app
