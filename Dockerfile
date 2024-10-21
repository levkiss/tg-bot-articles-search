# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files to disk (optional)
ENV PYTHONDONTWRITEBYTECODE 1
# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /usr/src/telegram_bot

# Install system dependencies (you might not need all of these, adjust as necessary)
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry - Dependency management tool
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to the PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy the Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Install Python dependencies using Poetry without development dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application code into the container
COPY . .

# Expose port (useful for webhooks or HTTP APIs)
EXPOSE 8443

# Define the command to run the application
CMD ["poetry", "run", "python3", "bot.py"]
