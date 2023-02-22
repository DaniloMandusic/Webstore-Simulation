import os
from datetime import timedelta

databaseUrl = os.environ["DATABASE_URL"]

class Configuration ( ):
    #SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3306/warehouse"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/warehouse"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    REDIS_HOST = os.environ["REDIS_PORT"]
    REDIS_PORT = 6397
    REDIS_PRODUCT_LIST = "products"

