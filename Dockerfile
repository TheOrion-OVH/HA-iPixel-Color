FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    bluetooth \
    bluez \
    libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5042

CMD ["python", "-m", "pypixelcolor.websocket"]
