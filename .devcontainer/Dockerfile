FROM mcr.microsoft.com/devcontainers/python:1-3.10-bullseye

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    echo 'export PATH="/home/vscode/.local/bin:$PATH"' >> /home/vscode/.bashrc

# Install additional tools
RUN apt-get update && apt-get install -y \
    git \
    make \
    vim \
    curl \
    wget \
    apt-transport-https \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Google Cloud SDK
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && apt-get install -y google-cloud-sdk && \
    rm -rf /var/lib/apt/lists/*

# Set Poetry to create virtualenvs in project
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Switch to vscode user
USER vscode

# Add Poetry to PATH for vscode user
RUN echo 'export PATH="/home/vscode/.local/bin:$PATH"' >> /home/vscode/.bashrc
