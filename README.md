# exif-app-backend

## What Is This?
This is the Flask backend for an image EXIF metadata viewing web application.

## Demo
![exif-web-app](https://github.com/flavius-t/exif-app-backend/assets/77416463/8f2a1bba-6d36-4352-8a90-9897b9976eb8)

## Setup

### Environment Variables
Ensure `.env` is present in repo root directory with the following fields:
```
DB_NAME=<database-name>
USERS_COLLECTION=<collection-name>
MONGO_USER=<mongo-server-root-username>
MONGO_PASSWORD=<mongo-server-root-password>
```

Note, authentication env vars for MongoDB for connecting to the MongoDB server must match those from `.env` in `exif-app-docker` repo.

### Dockerization
It is not recommended to build and run the container independently, as it depends on a MongoDB container as defined in `docker-compose.yaml` in the `exif-app-docker` repository.

### Dependencies
From repo root directory, run:
```
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

### Running App
```
python3 exif.py
```

Note, the commands shown above are intended for use inside the Docker container running this app. The app does not work outside the docker environment.
