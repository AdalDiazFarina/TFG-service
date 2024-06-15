import subprocess
from app.services.kafka_service import KafkaService
from app.services.json_service import load_data
from app.services.database_service import create_strategy_record, associate_strategies_with_profiles

def run():
  print("Starting kafka ....") 
  if kafka_is_running(): 
    print("Kafka is already active")
    run_kafka()
    return
  command = f'docker compose up -d'
  r = subprocess.run(command, shell=True, capture_output=True, text=True)
  if (r.returncode == 0):
    print(r.stdout)
    run_kafka()
  else:
    print("Command execution failed")
    print(r.stderr)

def kafka_is_running():
    try:
        output = subprocess.check_output(["docker", "ps", "-f", "name=kafka"])
        output_str = output.decode("utf-8")
        return 'kafka' in output_str
    except subprocess.CalledProcessError:
        return False
def run_kafka():
  print("Running kafka")
  kafka_service = KafkaService()
  kafka_service.receive('tasks')


def main():
    filename = 'app/data/strategies.json'
    data = load_data(filename)

    for strategy in data:
        name = strategy.get('name', '')
        description = strategy.get('description', '')
        model = strategy.get('model', '')
        if name and description and model:
            create_strategy_record(name, description, model)
        else:
            print("The object in the JSON file does not have complete 'name' and 'description' fields.")
    
    associate_strategies_with_profiles()

if __name__ == '__main__':
    main()
    run()