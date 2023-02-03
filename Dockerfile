# Dockerfile for the generating the whpool Docker image
FROM python:3.9.15-slim

COPY requirements.txt /opt/whpool/
WORKDIR /opt/whpool
RUN pip install -r requirements.txt
COPY . /opt/whpool/
RUN pip install -e .

ENTRYPOINT ["whpool"]