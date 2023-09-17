class Config:
    USERS_COLLECTION = "users"
    JWT_EXPIRATION_DELTA_MINS = 30
    JWT_REFRESH_WINDOW_MINS = 15


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    DB_NAME = "dev_exif_db"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    DB_NAME = "exif_db"
