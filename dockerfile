# Dockerfile - Streamlit app (lightweight, no Chrome)
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_PORT=8501

# Install system packages needed for common Python libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget curl unzip \
    libsndfile1 \
    libjpeg62-turbo-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Expose Streamlit port
EXPOSE 8501

# Final command
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
