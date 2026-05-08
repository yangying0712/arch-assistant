FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn loguru httpx pydantic
COPY api_gateway/ /app/api_gateway/
ENV PYTHONPATH=/app
EXPOSE 3000
CMD ["uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "3000"]
