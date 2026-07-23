FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir ckg-agentforce

CMD ["ckg-agentforce"]
