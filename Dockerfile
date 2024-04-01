FROM python:3.12

COPY ./src /app/src
COPY ./pyproject.toml /app/pyproject.toml

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
  build-essential \
  libatlas-base-dev \
  libgdal-dev \
  gfortran \
  make 

RUN cd /app && pip install .
