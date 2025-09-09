# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and app files
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 8080 for EB
EXPOSE 8080

# Set environment variable for Streamlit to use port 8080
ENV STREAMLIT_SERVER_PORT=8080

# Start Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]