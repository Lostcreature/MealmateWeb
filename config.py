import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'wdfghbdfhfhfhfhfhgdhsdhdfhfhfghgjkhgjg'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:admin@mysql_db/mealmate?charset=utf8mb4&collation=utf8mb4_general_ci'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
