FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    python3-dev \ 
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8502

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health

ENTRYPOINT ["streamlit", "run", "app/main.py", "--server.port=8502", "--server.address=0.0.0.0"]
