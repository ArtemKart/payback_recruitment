FROM python:3.11-slim

ARG WORKSPACE=/code

WORKDIR $WORKSPACE

COPY pyproject.toml $WORKSPACE

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -e .

COPY app $WORKSPACE/app/

EXPOSE 8000

CMD uvicorn app.infrastructure.api.main:app --host 0.0.0.0 --port 8000
