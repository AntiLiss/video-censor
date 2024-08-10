FROM python:3.12-alpine3.18

ENV PYTHONUNBUFFERED=1

COPY ./app /app
COPY ./requirements.txt /tmp/

COPY ./entrypoint.sh /

WORKDIR /app

EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client ffmpeg && \
    apk add --update --no-cache --virtual tmp-build-deps \
    build-base postgresql-dev musl-dev zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    apk del tmp-build-deps && \
    adduser --disabled-password --no-create-home main-user && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    chown -R main-user:main-user /vol && \
    chmod -R 755 /vol

RUN chmod +x /entrypoint.sh

ENV PATH="/py/bin:$PATH"

USER main-user

ENTRYPOINT ["/entrypoint.sh"]
