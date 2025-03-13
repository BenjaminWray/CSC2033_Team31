#!/usr/bin/bash

# install requirements
pip install -r requirements.txt

# perform database migrations
flask db init
flask db migrate
flask db upgrade

# run flask app
flask run --host=0.0.0.0 --port=5000