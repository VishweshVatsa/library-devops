# Containerized Library Management System with Automated CI/CD

Flask + PostgreSQL app, packaged with Docker, tested and deployed by GitHub Actions.

## Run locally (no Docker)
    pip install -r requirements.txt
    python app.py            # http://localhost:5000  (uses SQLite)

## Run tests
    pytest -v

## Run with Docker (app + PostgreSQL)
    docker compose up --build   # http://localhost:5000
    docker compose down         # stop (add -v to also delete the database)

## CI/CD (GitHub Actions)
Add these under GitHub repo > Settings > Secrets and variables > Actions:
- DOCKERHUB_USERNAME, DOCKERHUB_TOKEN
- EC2_HOST (public IP of your server), EC2_SSH_KEY (private key contents)

Every push to main: test -> build image -> push to Docker Hub -> deploy to EC2.
Pull requests only run the tests.
