# use python
FROM python:3.12

# create working directory
WORKDIR /app

# set environment variables
ENV PYTHONPATH="flaskr/"
ENV FLASK_APP="flaskr/app.py"

# execute startup shell script
CMD ["/usr/bin/bash", "-c", "./start_container.sh"]