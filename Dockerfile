# Dockerfile for the generating the whpool Docker image
FROM python:3.9.15-slim

RUN mkdir -p /opt/whpool
COPY . /opt/whpool
WORKDIR /opt/whpool
RUN pip install -r requirements.txt -e .

ENTRYPOINT ["/opt/whpool/whpool"]