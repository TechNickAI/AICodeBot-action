FROM python:3.11-slim

RUN apt-get update && apt-get install -y git

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY aicodebot_action.py /aicodebot_action.py
RUN chmod +x /aicodebot_action.py

ENTRYPOINT ["/aicodebot_action.py"]

