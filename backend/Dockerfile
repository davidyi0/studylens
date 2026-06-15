FROM python:3.12-slim

# Keep Python output unbuffered (logs show up immediately) and skip .pyc files.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install deps first so this layer caches unless requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code is bind-mounted in dev (see docker-compose.yml) so hot-reload works.
# Copying here keeps the image runnable on its own too.
COPY . .

EXPOSE 8000

# --reload picks up code changes from the bind mount during development.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
