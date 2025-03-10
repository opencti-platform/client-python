ARG BASE_IMAGE="python:3.12-alpine3.20"
FROM ${BASE_IMAGE}

# Install Python modules
# hadolint ignore=DL3003
COPY ./requirements.txt /opt/requirements.txt

RUN apk --no-cache add git build-base libmagic libffi-dev && \
    pip3 install --no-cache-dir -r /opt/requirements.txt && \
    apk del git build-base && rm /opt/requirements.txt

RUN adduser -D -g '' app
USER app