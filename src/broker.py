from faststream.rabbit import RabbitBroker, RabbitQueue
import os
from dotenv import load_dotenv



load_dotenv(dotenv_path=".env")

container_name_from_env = os.getenv('DB_TESTING_CONTAINER_NAME')

host = os.getenv('BROKER_HOST')
username = os.getenv('BROKER_USERNAME')
pwd = os.getenv('BROKER_PASSWORD')
port = os.getenv('BROKER_PORT')

broker = RabbitBroker(f"amqp://{username}:{pwd}@{host}:{port}/")

super_queue = RabbitQueue(name="super", durable=True)
publisher = broker.publisher(queue = super_queue)

"""@publisher
@broker.subscriber("empty_queue")
async def publish_to_queue(message: str)->str:
	print(f"Before return message. Body: {message}")
	return message"""