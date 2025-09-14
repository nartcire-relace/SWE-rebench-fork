FROM python:3.10-bookworm

RUN apt update && apt -y install podman

WORKDIR /SWE-bench

COPY . .

RUN pip install .
