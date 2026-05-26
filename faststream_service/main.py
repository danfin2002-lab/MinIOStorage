pip install 'faststream[kafka]' #TODO to requirements.txt

Before running the service, install FastStream CLI using the following command:
pip install "faststream[cli]" #TODO to requirements.txt


To run the service, use the FastStream CLI command and pass the module (in this case, the file where the app implementation is located) and the app symbol to the command.
faststream run basic:app --reload #TODO Change this string

#Publisher - издатель
#Subscriber - подписчик

from pydantic import BaseModel, Field, PositiveInt
from faststream import FastStream
from faststream.rabbit import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")#TODO to .env
app = FastStream(broker)

class User(BaseModel):
    user: str = Field(..., examples=["John"])
    user_id: PositiveInt = Field(..., examples=["1"])


@broker.subscriber("in-queue")
@broker.publisher("out-queue")
async def handle_msg(data: User) -> str:
    return f"User: {data.user} - {data.user_id} registered"
	
"""@broker.subscriber("in-queue")
@broker.publisher("out-queue")
async def handler(msg: RabbitMessage) -> None:
    await msg.ack()  # control brokers' acknowledgement p	
	
await broker.publish("Message", "in-queue")"""