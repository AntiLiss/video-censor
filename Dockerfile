FROM python:3.12.5-slim-bookworm

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./app /app
COPY ./requirements.txt /tmp/requirements.txt
COPY ./entrypoint.sh /entrypoint.sh
COPY ./data/ban_words /vol/static/ban_words
COPY ./data/gore-smoking-detector.pt /vol/static/gore-smoking-detector.pt

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        bash \
        postgresql-client \
        libpq-dev \
        build-essential \
        libffi-dev \
        ffmpeg \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Python dependencies
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /tmp

# Create user and configure file system
RUN adduser --disabled-password main-user && \
    mkdir -p /vol/media /tmp-files && \
    chown -R main-user:main-user /vol /tmp-files /entrypoint.sh && \
    chmod -R 775 /vol /tmp-files /entrypoint.sh

USER main-user

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
