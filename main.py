import subprocess
from app.services.kafka_service import KafkaService

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

if __name__ == '__main__':
    run()
