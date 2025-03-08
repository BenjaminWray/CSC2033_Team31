# use python
FROM python:latest

# create working directory
WORKDIR /app

# install requirements
ADD requirements.txt .
RUN pip install -r requirements.txt

# add project files
ADD flaskr flaskr
ADD tests tests
ADD .env .

# set environment variables
ENV PYTHONPATH="flaskr/"
ENV FLASK_APP="flaskr/app.py"

# create database migrations files
RUN flask db init

# execute startup shell script
ADD start_container.sh .
CMD ["/usr/bin/bash", "-c", "./start_container.sh"]