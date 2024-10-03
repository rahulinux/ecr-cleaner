FROM python:3.12-slim
ARG PROJECT_NAME
ARG VERSION

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && apt-get autoclean -y \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/* \
    ;

WORKDIR /app

COPY dist /app/dist

RUN pip install --no-cache-dir "/app/dist/${PROJECT_NAME}-${VERSION}-py3-none-any.whl[cli]"

ENTRYPOINT ["python", "/usr/local/bin/demo-cli"]
