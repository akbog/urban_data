import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "password"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASKY_ADMIN = os.environ.get('URBAN_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SYSTEM_ADMIN = os.environ.get('SYSTEM_ADMIN')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')

config = {
    'development':DevelopmentConfig,

    'default':DevelopmentConfig
}
