# -----------------------------
# 1) Base Image
# -----------------------------
FROM python:3.10-slim

# -----------------------------
# 2) Install system dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    chromium \
    chromium-driver
    xvfb \
    mesa-utils \
    fonts-liberation \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
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

# -----------------------------
# 3) Install Google Chrome
# -----------------------------
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# -----------------------------
# 4) Install ChromeDriver
# -----------------------------
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE") && \
    wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

# -----------------------------
# 5) Create project folder
# -----------------------------
WORKDIR /app

# -----------------------------
# 6) Copy dependency list
# -----------------------------
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------
# 7) Copy project files
# -----------------------------
COPY . .

# -----------------------------
# 8) Streamlit environment vars
# -----------------------------
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_PORT=10000
ENV PYTHONUNBUFFERED=1

# -----------------------------
# 9) Expose service port
# -----------------------------
EXPOSE 10000

# -----------------------------
# 10) Start the app
# -----------------------------
CMD ["streamlit", "run", "streamlit_app.py", "--server.headless=true", "--server.port=10000"]

