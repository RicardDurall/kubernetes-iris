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
    && rm -rf /var/lib/apt/lists/*

# Set Poetry to create virtualenvs in project
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Switch to vscode user
USER vscode

# Add Poetry to PATH for vscode user
RUN echo 'export PATH="/home/vscode/.local/bin:$PATH"' >> /home/vscode/.bashrc
