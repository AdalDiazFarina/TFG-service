from confluent_kafka import Consumer, KafkaError, Producer
import os
from dotenv import load_dotenv
import json

load_dotenv()
BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS")

class KafkaService:
    def __init__(self, bootstrap_servers=BOOTSTRAP_SERVERS):
        self.bootstrap_servers = bootstrap_servers

    def send(self, topic, message):
        producer = Producer({'bootstrap.servers': self.bootstrap_servers})
        producer.produce('completed_tasks', json.dumps(message).encode('utf-8'))
        producer.flush()

    def receive(self, topic):
        consumer = Consumer({
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': 'my_consumer_group',
            'auto.offset.reset': 'earliest'
        })
        consumer.subscribe(['tasks'])
        try:
            while True:
                message = consumer.poll(timeout=1.0)
                if message is None:
                    continue
                if message.error():
                    if message.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(message.error())
                        break
        
            print('- Received message ...')
            # messageData = json.loads(message.value.decode('utf-8'))
            # result = validateMessage(model, messageData)
            print('- Validation successful!!!')
            send('completed_tasks', message)
    
        except KeyboardInterrupt:
            pass
        
        finally:
            consumer.close()

    def validateMessage(self, model, message):
        ## TODO: Validar el modelo
        ## TODO: Guardar los resultados en la base de datos
        ## TODO: Mensaje terminado validación
        print('- Validating message ...')
        print('######################')
        return {"message": "Validation successful!", "code": 1}