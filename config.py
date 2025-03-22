import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'acdd6a4ed3cbaa196149e1fab515d1b56b6f6c43d66f42c8ea2829bf3cbf2bd0'

class DevelopmentConfig(Config):
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'database', 'dev.db')