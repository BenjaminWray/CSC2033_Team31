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
ADD .env .env

# set environment variables
ENV PYTHONPATH="flaskr/"
ENV FLASK_APP="flaskr/app.py"

# create database migrations files
RUN flask db init

# run flask application
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]