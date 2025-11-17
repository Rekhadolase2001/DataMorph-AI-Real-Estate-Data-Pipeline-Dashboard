FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# ---------- System packages ----------
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-distutils python3-venv \
    wget curl unzip gnupg xvfb \
    libnss3 libxss1 libasound2 libatk1.0-0 \
    libatk-bridge2.0-0 libgbm1 libxcomposite1 \
    libxdamage1 libxrandr2 libxkbcommon0 \
    fonts-liberation ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ---------- Install Chrome (Stable) ----------
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# ---------- Install ChromeDriver ----------
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    DRIVER_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_VERSION) && \
    wget -q https://storage.googleapis.com/chrome-for-testing-public/$DRIVER_VERSION/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm -rf chromedriver-linux64.zip chromedriver-linux64

# ---------- App directory ----------
WORKDIR /app

# ---------- Install Python dependencies ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Copy app ----------
COPY . .

EXPOSE 8501

# ---------- Run Streamlit ----------
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
