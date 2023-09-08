class Config:
    USERS_COLLECTION = "users"


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    DB_NAME = "dev_exif_db"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    DB_NAME = "exif_db"
