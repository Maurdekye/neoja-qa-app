# neoja-qa-app

A simple dockerized Q&A app running on a Flask backend & a Flutter frontend, using a MongoDB document based database.

# Build steps

1. Ensure Docker is installed.
2. Copy the provided `.env.sample` file into a `.env` file, and set the `SECRET_KEY` variable to a secret key value.
3. Naviate into the `backend/` directory and provide or generate a cert & key pair for https communication, such as with the command `openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem`
4. navigate to the root directory and run `docker-compose up` to build and start up all relevant services.
5. navigate to `https://localhost:8080` to use the app.