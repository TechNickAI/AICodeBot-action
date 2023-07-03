FROM python:3.11-slim

RUN apt-get update && apt-get install -y git

RUN pip install aicodebot

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

