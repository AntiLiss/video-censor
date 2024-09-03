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
    rm -rf /tmp && \
    adduser --disabled-password main-user && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    mkdir -p /tmp-files && \
    chown -R main-user:main-user \
        /tmp-files \
        /vol \
        /home  && \
    chmod -R 755 \
        /tmp-files \
        /vol \
        /home  && \
    chmod +x /entrypoint.sh

COPY ./ban_words /vol/web/static/ban_words
COPY ./gore-smoking-detector.pt /vol/web/static

ENV PATH="/py/bin:$PATH"

USER main-user

ENTRYPOINT ["/entrypoint.sh"]
