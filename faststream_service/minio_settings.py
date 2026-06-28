from minio import Minio
#pip install python-dotenv
import os
from dotenv import load_dotenv


# Загружаем переменные из .env в окружение
load_dotenv()

MIO_ENDPOINT = os.getenv("MIO_ENDPOINT")
MIO_ACCESS_KEY = os.getenv("MIO_ACCESS_KEY")
MIO_SECRET_KEY = os.getenv("MIO_SECRET_KEY")
MIO_BUCKET_NAME = os.getenv("MIO_BUCKET_NAME")

client = Minio(
    endpoint=MIO_ENDPOINT,
    access_key=MIO_ACCESS_KEY,
    secret_key=MIO_SECRET_KEY,
    secure=False,
)

bucket_name = MIO_BUCKET_NAME

found = client.bucket_exists(bucket_name)
if not found:
    client.make_bucket(bucket_name)
    print("Created bucket", bucket_name)
else:
    print("Bucket", bucket_name, "already exists")