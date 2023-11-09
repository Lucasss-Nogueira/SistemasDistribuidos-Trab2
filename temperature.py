from confluent_kafka import Producer
import grpc
import futures
import home_assistant_pb2
import home_assistant_pb2_grpc
import time

temperature = 25  # Inicia com 25 graus Celsius

class TemperatureActuatorService(TemperatureActuatorServiceServicer):
    def alterarTemperatura(ActuatorCommand):

        temperature = ActuatorCommand.temperature
    
        return home_assistant_pb2.Empty(message="Comando executado com sucesso.")

server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=10))
home_assistant_pb2_grpc.add_TemperatureActuatorServiceServicer_to_server(TemperatureActuatorService(), server)
server.add_insecure_port('[::]:50054')
server.start()  

def publish_temperature_data():
    producer_conf = {'bootstrap.servers': 'localhost:9092'}
    producer = Producer(producer_conf)
    topic = 'fila_temperatura'

    global temperature

    while True:
        
        message = f"Temperatura: {temperature}°C"
        producer.produce(topic, message.encode('utf-8'))
        producer.flush()
        time.sleep(5)

publish_temperature_data()
