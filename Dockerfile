FROM python:3.12-slim

# Create a non-root user for security (Hugging Face requirement)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install git as a root user temporarily
USER root
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
USER user

# Install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy all files
COPY --chown=user . .

# HF Spaces strictly uses port 7860
ENV PORT=7860
EXPOSE 7860

# This starts your OpenEnv server
CMD ["python", "app.py"]