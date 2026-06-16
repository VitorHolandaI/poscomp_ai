FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# poppler-utils: pdftotext / pdftocairo | tesseract + por/eng: OCR de gabaritos
RUN apt-get update && apt-get install -y --no-install-recommends \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-por \
        tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Dependências primeiro (camada cacheável)
COPY pyproject.toml uv.lock README.md ./
COPY poscomp_app ./poscomp_app
RUN uv sync --frozen --no-dev

# Conteúdo da aplicação + provas de origem
COPY templates ./templates
COPY static ./static
COPY Provas-POSCOMP ./Provas-POSCOMP

# Processa TODAS as provas no build e guarda como seed da imagem
RUN uv run python -m poscomp_app.seed && mv var var_seed

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "poscomp_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
