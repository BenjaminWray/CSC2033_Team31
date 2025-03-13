# use python
FROM python:latest

# create working directory
WORKDIR /app

# set environment variables
ENV PYTHONPATH="flaskr/"
ENV FLASK_APP="flaskr/app.py"

# execute startup shell script
CMD ["/usr/bin/bash", "-c", "./start_container.sh"]