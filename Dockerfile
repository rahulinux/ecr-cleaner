FROM --platform=$BUILDPLATFORM python:3.13-slim AS builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    # Allow statements and log messages to appear immediately
    PYTHONUNBUFFERED=1 \
    # disable a pip version check to reduce run-time & log-spam
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # cache is useless in docker image, so disable to reduce image size
    PIP_NO_CACHE_DIR=1

RUN set -ex \
    && apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential \
    curl \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && apt-get autoclean -y \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/* \
    ;

WORKDIR /app
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
COPY . /app
RUN /usr/local/bin/task install
RUN /usr/local/bin/task build

FROM --platform=$BUILDPLATFORM python:3.13-alpine

ENV PIP_DEFAULT_TIMEOUT=100 \
    # Allow statements and log messages to appear immediately
    PYTHONUNBUFFERED=1 \
    # disable a pip version check to reduce run-time & log-spam
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # cache is useless in docker image, so disable to reduce image size
    PIP_NO_CACHE_DIR=1

RUN set -ex \
    && addgroup --system --gid 30000 appuser \
    && adduser --system --uid 30000 --no-create-home appuser \
    && mkdir -p /app \
    && chown -R appuser:appuser /app

WORKDIR /app

COPY --from=builder /app/dist /app/dist

# Install any wheel files with the 'cli' extra
RUN find /app/dist/ -type f -name '*.whl' -exec pip install --no-cache-dir {}[cli] \;

USER appuser

ENTRYPOINT ["python", "/usr/local/bin/ecr-cleaner"]
