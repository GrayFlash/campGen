# Backend Description

Trying to rebuild the stuffs here. `docker-compose.yaml` to contain the necessary DB info, `dev.env` to contain the environment variables for the dev setup done locally.

`.env` files still remains hidden via gitignore and contains `API_KEYS` and other critical secrets.

## Environment Setup

- ```docker-compose --env-file dev.env up```, for starting the MySQL database locally.
- ```./createDB_test.sh``` for setting up dummy data into the database.
- Create a ViretualEnv with, ```python3 -m venv env```.
- Activate virtual env, ```source env/bin/activate```.
- ```pip install -r requirements.txt```, for installing the dependencies.
- To export development environment, ```export FLASK_ENV=development```.
- To start the flask server, ```flask run```.
