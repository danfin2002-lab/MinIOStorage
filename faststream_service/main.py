#TODO Заворачиваю всё в докер
import os

from dotenv import load_dotenv
from faststream.rabbit import RabbitBroker
from faststream import FastStream
from faststream.rabbit import RabbitQueue
from utils.check_filetype import check_filetype
from minio_settings import client, bucket_name
from AIPart.base import process_image, save_new_image


load_dotenv(dotenv_path=".env")

container_name_from_env = os.getenv('DB_TESTING_CONTAINER_NAME')

host = os.getenv('BROKER_HOST')
username = os.getenv('BROKER_USERNAME')
pwd = os.getenv('BROKER_PASSWORD')
port = os.getenv('BROKER_PORT')

broker = RabbitBroker(f"amqp://{username}:{pwd}@{host}:{port}/")
#broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = FastStream(broker)

file_path = ""

super_queue = RabbitQueue(name="super", durable=True)
#В этом файле это будет единственная функция
@broker.subscriber(super_queue)
async def handle_msg(msg_body: str):
	print("All is Okey!!!")
	print(msg_body)
	file_path = msg_body
	file_is_image = check_filetype(client, bucket_name, file_path)
	print(f"Файл является изображением: {file_is_image}")
	if not file_is_image:
		print("Файл не является изображением")
		return
	new_image = process_image(client, bucket_name, file_path)
	await save_new_image(client, bucket_name, file_path, new_image)