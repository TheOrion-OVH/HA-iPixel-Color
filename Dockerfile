FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    bluetooth \
    bluez \
    libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir pypixelcolor

EXPOSE 5042

CMD ["python", "-m", "pypixelcolor.websocket"]
