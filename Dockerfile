FROM python:3.11-slim

RUN apt-get update && apt-get install -y git jq

RUN pip install aicodebot
# Additional dependencies for aicodebot_action
RUN pip install PyGithub

COPY aicodebot_action.py /aicodebot_action.py

RUN chmod +x /aicodebot_action.py

ENTRYPOINT ["/aicodebot_action.py"]

