FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY apisaas ./apisaas
ENV APISAAS_DB=/data/apisaas.db
VOLUME /data
EXPOSE 8000
CMD ["uvicorn", "apisaas.app:app", "--host", "0.0.0.0", "--port", "8000"]
