import os
import json
import nbformat
from string import Template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.investment_profile_model import InvestmentProfile
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
from confluent_kafka import Consumer, KafkaError, Producer
from dotenv import load_dotenv
from app.services.json_service import load_data, save_data
from app.services.database_service import updateInvestmentProfileStrategy, getModelName, create_operations

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
    filename = './app/data/result.json'
    variables = createVariables(message['profile_id'], message['strategy_id'], message['duration'])
    if 'code' in variables and variables['code'] == -1:
        print(f"Failed to create variables: {variables['message']}")
        return {"message": "Error", "code": -1, "strategy_id": message['strategy_id'], "profile_id": message['profile_id']}
    else:
        variables = {k: str(v) for k, v in variables.items()}
        runNotebook('app/notebooks/' + getModelName(message['strategy_id']) + '.ipynb', variables)
        data = load_data(filename)
        updateInvestmentProfileStrategy(message['profile_id'], message['strategy_id'], data)
        filename = './app/data/operation.json'
        data = load_data(filename)
        create_operations(message['profile_id'], message['strategy_id'], data)
        save_data([], filename)
        print('- Validating message ...')
        # print('######################')
        return {"message": "Validation successful!", "code": 1, "strategy_id": message['strategy_id'], "profile_id": message['profile_id']}
    

def runNotebook(route, variables):
    try:
        # Leer el contenido del cuaderno como una cadena de texto
        with open(route, 'r', encoding='utf-8') as f:
            notebook_content = f.read()

        # Crear plantilla del cuaderno
        notebook_template = Template(notebook_content)

        # Sustituir marcadores de posición con los valores reales
        notebook_content_with_values = notebook_template.safe_substitute(variables)

        # Convertir la cadena de texto de vuelta a un objeto NotebookNode
        notebook = nbformat.reads(notebook_content_with_values, as_version=4)

        # Ejecutar el cuaderno
        runner = ExecutePreprocessor(timeout=None)
        runner.preprocess(notebook, {'metadata': {'path': os.path.dirname(route)}})

    except Exception as e:
        print(f"Error during notebook execution: {e}")

def createVariables(profile_id, strategy_id, duration):
    engine = create_engine("postgresql://root:1234@localhost:5432/FundFlowForge")
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        profile = session.query(InvestmentProfile).get(profile_id)
        session.close()

        return {
            'profile_id': profile_id,
            'strategy_id': strategy_id,
            'initial_capital': float(profile.initial_capital),
            'monthly_contribution': float(profile.monthly_contribution),
            'duration': int(duration)
            }
    except Exception as e:
        session.close()
        print(f"Error retrieving profile: {e}")
        return {'code': -1, 'message': str(e)}


