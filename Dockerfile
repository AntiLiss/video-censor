FROM python:3.12.5-slim-bookworm

ENV PYTHONUNBUFFERED=1

COPY ./app /app
COPY ./requirements.txt /tmp/
COPY ./entrypoint.sh /
COPY ./data/ban_words ./data/gore-smoking-detector.pt /vol/static/

WORKDIR /app

RUN \
    # Linux deps
    apt-get update && \
    apt-get install -y --no-install-recommends \
        bash \
        postgresql-client \
        libpq-dev \
        build-essential \
        libffi-dev \
        ffmpeg \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/* && \
    # Python deps
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /tmp/* && \
    # Create user and configure file system
    mkdir -p /vol/media /tmp/tmp-files && \
    adduser --disabled-password main-user && \
    chown -R main-user:main-user /vol /tmp/tmp-files /entrypoint.sh && \
    chmod -R 775 /vol /tmp/tmp-files /entrypoint.sh

USER main-user

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
