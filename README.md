# neoja-qa-app

A simple dockerized Q&A app running on a Flask backend & a Flutter frontend, using a MongoDB document based database.

# Build steps

1. Ensure Docker is installed.
2. Copy the provided `.env.sample` file into a `.env` file, and set the `SECRET_KEY` variable to a secret key value.
4. Run `docker-compose up` to build and start up all relevant services.
5. navigate to `http://localhost` to use the app.

# Todo

* Integrate a more widely used state engine into frontend
* Possibly refactor database interactions to use a single key system