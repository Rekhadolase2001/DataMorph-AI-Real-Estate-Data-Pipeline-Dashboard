# -----------------------------
# 1) Base Image
# -----------------------------
FROM python:3.10-slim

# -----------------------------
# 2) Install system dependencies + Chrome + Chromedriver
# -----------------------------
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    chromium \
    chromium-driver \
    xvfb \
    fonts-liberation \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgbm1 \
    libasound2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libxss1 \
    libxshmfence1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome Stable
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# -----------------------------
# 3) Set working directory
# -----------------------------
WORKDIR /app

# -----------------------------
# 4) Install Python dependencies
# -----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------
# 5) Copy project
# -----------------------------
COPY . .

# -----------------------------
# 6) Streamlit configuration
# -----------------------------
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_HEADLESS=true

EXPOSE 8080

# -----------------------------
# 7) Start Streamlit
# -----------------------------
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.enableCORS=false"]
