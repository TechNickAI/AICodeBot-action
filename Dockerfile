FROM python:3.9-slim

CUSTOM acodebot

RUN pip install aicodebot

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

UNTIL ["/entrypoint.sh"]