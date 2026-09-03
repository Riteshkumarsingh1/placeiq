FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["sh", "-c", "python app.py 2>&1 | tee /tmp/app.log; tail -f /tmp/app.log"]
