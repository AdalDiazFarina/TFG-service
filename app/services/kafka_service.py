import os
import json
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
from confluent_kafka import Consumer, KafkaError, Producer
from dotenv import load_dotenv
# from app.services.json_service import load_data
# from app.services.database_service import updateInvestmentProfileStrategy, getModelName, create_operations

load_dotenv()
BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS")

class KafkaService:
    def __init__(self, bootstrap_servers=BOOTSTRAP_SERVERS):
        self.bootstrap_servers = bootstrap_servers

    def send(self, topic, message):
        producer = Producer({'bootstrap.servers': self.bootstrap_servers})
        producer.produce(topic, json.dumps(message).encode('utf-8'))
        producer.flush()

    def receive(self, topic):
        consumer = Consumer({
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': 'my_consumer_group',
            'auto.offset.reset': 'earliest'
        })
        consumer.subscribe([topic])
        try:
            while True:
                message = consumer.poll(timeout=1.0)
                if message != None:
                    respond = validateMessage(message.value().decode('utf-8'))
                    self.send('completed_tasks', respond)
                if message is None:
                    continue
                if message.error():
                    if message.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(message.error())
                        break

        except KeyboardInterrupt:
            pass
        
        finally:
            consumer.close()




def validateMessage(message):
    message = json.loads(message)
    ## TODO: Validar el modelo
    ## TODO: Guardar los resultados en la base de datos
    ## TODO: Mensaje terminado validación
    # filename = './app/data/result.json'
    # runNotebook('app/notebooks/' + getModelName(message['strategy_id']) + '.ipynb')
    # data = load_data(filename)
    # updateInvestmentProfileStrategy(message['profile_id'], message['strategy_id'], data)
    # filename = './app/data/operations.json'
    # data = load_data(filename)
    # create_operations(message['profile_id'], message['strategy_id'], data)
    # print('- Validating message ...')
    # print('######################')
    # return {"message": "Validation successful!", "code": 1, "strategy_id": message['strategy_id'], "profile_id": message['profile_id']}
    

def runNotebook(route):
    with open(route, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)
    
    runner = ExecutePreprocessor(timeout=None)
    runner.preprocess(notebook, {'metadata': {'path': os.path.dirname(route)}})
    