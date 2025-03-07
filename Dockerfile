# Use Python as the base image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 8080

# Start the Flask app
CMD ["python", "app.py"]
