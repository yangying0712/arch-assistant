FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn loguru httpx pydantic
COPY orchestration_engine/ /app/orchestration_engine/
ENV PYTHONPATH=/app
EXPOSE 8001
CMD ["uvicorn", "orchestration_engine.main:app", "--host", "0.0.0.0", "--port", "8001"]
