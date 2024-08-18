FROM python:3.12.5-slim-bookworm

ENV PYTHONUNBUFFERED=1

COPY ./app /app
COPY ./requirements.txt /tmp/
COPY ./entrypoint.sh /

WORKDIR /app

EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apt-get update && \
    apt-get install -y \
        bash \
        postgresql-client \
        libpq-dev \
        build-essential \
        libffi-dev \
        ffmpeg \
        zlib1g-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/* && \
    adduser --disabled-password main-user && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    chown -R main-user:main-user \
        /tmp \
        /vol \
        /home  && \
    chmod -R 755 \
        /tmp \
        /vol \
        /home  && \
    chmod +x /entrypoint.sh

ENV PATH="/py/bin:$PATH"

USER main-user

ENTRYPOINT ["/entrypoint.sh"]
