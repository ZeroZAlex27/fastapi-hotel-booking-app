FROM python:3.12-slim

# Prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy dependency file
COPY pyproject.toml poetry.lock* /app/

# Install Poetry and dependencies
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy the rest of the application
COPY . .

# Make shell scripts executable
RUN chmod +x /app/docker/*.sh

# Default command
CMD ["/app/docker/app.sh"]