# neoja-qa-app

A simple dockerized Q&A app running on a Flask backend & a Flutter frontend, using a MongoDB document based database.

# Build steps

1. Ensure Docker is installed.
2. Copy the provided `.env.sample` file into a `.env` file, and set the `SECRET_KEY` variable to a secret key value.
4. Run `docker compose up` to build and start up all relevant services.
5. Navigate to `http://localhost` in a web browser to use the app.

Each of the three components, the database, backend, and frontend, can be run independently of one another if necessary, with the respective commands `docker compose up database`, `docker compose up backend`, and `docker compose up backend`.