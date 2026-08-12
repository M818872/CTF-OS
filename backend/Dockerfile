FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive \
    CTF_OS_SOLVER_MAX_STEPS=48 \
    CTF_OS_SOLVER_MAX_LINKS=24 \
    CTF_OS_AUTO_INSTALL=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates curl file binutils unzip zip p7zip-full exiftool binwalk nmap \
      tshark poppler-utils steghide fcrackzip john jq ripgrep xxd \
      ruby ruby-dev git wget dnsutils whois tcpdump gobuster ffuf sqlmap \
      openssl gdb checksec && \
    rm -rf /var/lib/apt/lists/*

COPY backend/pyproject.toml ./backend/pyproject.toml
COPY sdk ./sdk
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ./sdk ./backend

COPY backend/app ./backend/app

WORKDIR /app/backend
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
