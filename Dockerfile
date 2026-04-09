# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: dependencies
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: runtime
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY app_gradiov4.py config.py models.py ./
COPY core/       ./core/
COPY components/ ./components/

# Copy recipe dataset
COPY data/recetas_backend_proceso_ultra.json ./data/

RUN mkdir -p data

EXPOSE 8080

CMD ["python", "app_gradiov4.py"]