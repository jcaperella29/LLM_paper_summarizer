# Use a lightweight Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy all files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask's port
EXPOSE 8080

# Start the Flask app
CMD ["python", "app.py"]
