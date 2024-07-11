# Tool for the analysis of long-term investment strategies for different financial profiles.

This project is a service developed in Python that defines investment strategies, metrics, and includes a Kafka messaging system, which is also dockerized. The service can be started with a single command.

## Author
- Adal Díaz Fariña
## Features
- Investment Strategies: Predefined strategies for investment.
- Metrics: System to measure and analyze different financial metrics.
- Kafka Messaging System: Dockerized Kafka for messaging.
## Technologies Used
- Python: The programming language used for the service.
- Kafka: A distributed streaming platform used for messaging.
- Docker: Used to containerize the Kafka messaging system.
## Getting Started
To get a local copy of the project up and running, follow these steps:

### Prerequisites
- Python: Make sure you have Python installed. You can download it from python.org.
- Docker: Ensure you have Docker installed. You can download it from docker.com.
### Installation
1. Clone the repository:
```sh 
git clone git@github.com:AdalDiazFarina/TFG-service.git
```
2. Create a virtual environment:
```sh 
python -m venv venv
```
3. Activate the virtual environment:
- On Windows:
```sh 
venv\Scripts\activate
```
- On macOS and Linux:
```sh 
source venv/bin/activate
```
5. Install dependencies:
```sh 
pip install -r requirements.txt
```
## Usage
- Start Service: Run python main.py to start the service.