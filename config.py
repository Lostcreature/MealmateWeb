import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'wdfghbdfhfhfhfhfhgdhsdhdfhfhfghgjkhgjg'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:admin@localhost/mealmate'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
