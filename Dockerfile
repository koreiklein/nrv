FROM python:3.7.1

RUN apt-get update

RUN mkdir -p /main
WORKDIR /main

RUN pip install pipenv

# COPY Pipfile .
# COPY Pipfile.lock .

# RUN pipenv install

