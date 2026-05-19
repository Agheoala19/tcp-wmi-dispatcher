FROM python:3.9-slim
WORKDIR /app
COPY server.py .
EXPOSE 8721
CMD ["python", "server.py"]