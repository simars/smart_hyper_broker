FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Install Node.js mapping to current LTS (20.x)
ENV NODE_VERSION=20.x
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION} | bash - && \
    apt-get install -y nodejs

# Install tools and utilities
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install global node packages like pnpm or yarn if needed
RUN npm install -g pnpm
