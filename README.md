# exif-app-backend

## What Is This?
This is the Flask backend for an image EXIF metadata viewing web application.

## Demo
![exif-web-app](https://github.com/flavius-t/exif-app-backend/assets/77416463/8f2a1bba-6d36-4352-8a90-9897b9976eb8)

## Setup

### Environment Variables
Ensure `.env` is present in local repo root directory with the following fields:
```
MONGO_USER=<mongo-server-root-username>
MONGO_PASSWORD=<mongo-server-root-password>
FLASK_ENV=<development/production>
FLASK_SECRET_KEY=<your-flask-secret-key>
```

## MongoDB Connections
The backend must connect to two different MongoDB servers, depending on the situation, as shown in the diagram below.
![exif-backend-mongo](https://github.com/flavius-t/exif-app-backend/assets/77416463/d8bc7d07-d894-481e-9020-723208b82642)
    
The following environment variables must be defined:
- `MONGO_URI`:
    * Used for connecting to local or remote MongoDB servers. The local server is accessed over Docker network, while the remote CI server is accessed over local host network:
        * connecting to local server: defined in `exif-app-docker/docker-compose.yml`
        * connecting to remote server: defined in `.github/workflows/pytest-tests.yml`
- `DB_NAME`: `config.py`
    * defines the name of the database to be used and/or created by the app, both on local and remote (CI) environments. Note, this defaults to the same development database name for both local dev and remote CI environments.
- `USERS_COLLECTION`: `config.py`
    * defines the name of the collection storing users. It is not required for the local dev/prod environments to define different names for this.
- `MONGO_USER`, `MONGO_PASSWORD`: `.env`, `.github/workflows/pytest-tests.yml`
    * used in `utils.mongo_utils.py` for authenticating against the local/remote mongoDB servers. These do not need to match each other.
    * Auth details for the local server must exactly match those defined in the `exif-app-docker` repository.
---

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
