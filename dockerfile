FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg xvfb \
    libnss3 libxss1 libasound2 libatk1.0-0 \
    libatk-bridge2.0-0 libgbm1 libxcomposite1 \
    libxdamage1 libxrandr2 libxkbcommon0 \
    fonts-liberation ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome Stable
RUN LATEST=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['channels']['Stable']['version'])") \
    && wget -q https://storage.googleapis.com/chrome-for-testing-public/$LATEST/linux64/chrome-linux64.zip \
    && unzip chrome-linux64.zip \
    && mv chrome-linux64 /opt/chrome \
    && ln -s /opt/chrome/chrome /usr/bin/google-chrome \
    && rm chrome-linux64.zip

# Install Chromedriver
RUN LATEST=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['channels']['Stable']['version'])") \
    && wget -q https://storage.googleapis.com/chrome-for-testing-public/$LATEST/linux64/chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm -rf chromedriver-linux64 zip

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
