#!/usr/bin/bash

# perform database migrations
flask db migrate
flask db upgrade

# run flask app
flask run --host=0.0.0.0 --port=5000