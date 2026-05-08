FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn loguru httpx pydantic
COPY llm_router/ /app/llm_router/
ENV PYTHONPATH=/app
EXPOSE 8002
CMD ["uvicorn", "llm_router.main:app", "--host", "0.0.0.0", "--port", "8002"]
