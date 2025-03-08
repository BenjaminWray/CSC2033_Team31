# How to run the program and database with docker:

## Step 1: Install and run Docker
Download and install Docker Desktop from https://www.docker.com/
<img src="\screenshots\install_docker_desktop.png" alt="" width="1280"/>

## Step 2: Install docker plugin (PyCharm community only)
If you are using PyCharm professional you can skip this step as the docker plugin should already be installed.

In PyCharm, go to **Settings > Plugins > Marketplace** and install Docker
<img src="\screenshots\install_docker_plugin.png" alt="" width="1280"/>

## Step 3: Run docker containers
Make sure Docker Desktop is running, then open **docker-compose.yaml** and click the double arrow at the top of the file to run the containers.
<img src="\screenshots\run_docker-compose.png" alt="" width="1280"/>

Docker will set up and run the database and flask app for you. You can access the web page at http://127.0.0.1:5000.
<img src="\screenshots\docker_containers.png" alt="" width="1280"/>

After running **docker-compose.yaml** once, PyCharm will automatically add the file to the run configurations so you can run the containers anytime without needing to open the docker-compose file.
<img src="\screenshots\run_configuration.png" alt="" width="1280"/>
