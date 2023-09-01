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
```

Note, authentication env vars used in `mongo_utils.py` for connecting to the MongoDB server are provided by `.env` in `exif-app-docker` repo.

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
