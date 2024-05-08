import subprocess
from app.notebooks.services.kafka_service import KafkaService
from app.notebooks.services.json_service import load_data
from app.notebooks.services.database_service import create_strategy_record, associate_strategies_with_profiles

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
  kafka_service.receive('completed_tasks')


def main():
    filename = 'app/data/strategies.json'
    data = load_data(filename)

    for strategy in data:
        name = strategy.get('name', '')
        description = strategy.get('description', '')
        if name and description:
            create_strategy_record(name, description)
        else:
            print("The object in the JSON file does not have complete 'name' and 'description' fields.")
    
    associate_strategies_with_profiles()

if __name__ == '__main__':
    main()
    run()
