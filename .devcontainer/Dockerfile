ARG VARIANT
FROM mcr.microsoft.com/devcontainers/python:1-${VARIANT}

# Additional OS packages
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    fzf \
    gnupg2 \
    jq \
    vim \
    ;

# Install shellcheck
RUN scversion="stable" && \
    wget -qO- "https://github.com/koalaman/shellcheck/releases/download/${scversion?}/shellcheck-${scversion?}.linux.x86_64.tar.xz" | tar -xJv && \
    cp "shellcheck-${scversion}/shellcheck" /usr/bin/ && \
    shellcheck --version

USER vscode
