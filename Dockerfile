FROM python:3.12-slim AS base

WORKDIR /app
RUN mkdir AnyLog-API
COPY anylog_api /app/AnyLog-API/anylog_api
COPY setup.* /app/AnyLog-API/
COPY requirements.txt /app/AnyLog-API/

RUN apt-get -y update && \
    python3 -m pip install --upgrade pip build twine && \
    python3 -m pip install --upgrade -r ./AnyLog-API/requirements.txt

WORKDIR /app/AnyLog-API
RUN python -m build &&  \
    mv /app/AnyLog-API/dist/anylog_api-1.0.0-py2.py3-none-any.whl /app/anylog_api-1.0.0-py2.py3-none-any.whl

WORKDIR /app
RUN rm -rf /app/AnyLog-API/ && \
    python3 -m pip install --upgrade /app/anylog_api-1.0.0-py2.py3-none-any.whl

ENTRYPOINT ["/bin/bash"]
