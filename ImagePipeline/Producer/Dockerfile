FROM ubuntu:22.04

WORKDIR /app

COPY . .

RUN apt update && apt install -y python3-pip && pip3 install -r requirements.txt

CMD ["gunicorn", "server_fast:app", "--workers 5", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--keep-alive", "60", "--backlog", "81"]
