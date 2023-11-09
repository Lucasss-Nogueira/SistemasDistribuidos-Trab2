from confluent_kafka import Producer
import grpc
import home_assistant_pb2
import futures
import home_assistant_pb2_grpc
import time

luminosity = 150  # Inicia com o máximo de luminosidade 

class LuminosityActuatorService(LuminosityActuatorServiceServicer):
    def alterarLuminosidade(ActuatorCommand):

        luminosity = ActuatorCommand.luminosity
    
        return home_assistant_pb2.Empty(message="Comando executado com sucesso.")

server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=10))
home_assistant_pb2_grpc.add_LuminosityActuatorServiceServicer_to_server(LuminosityActuatorService(), server)
server.add_insecure_port('[::]:50055')
server.start()  

def publish_luminosity_data():
    producer_conf = {'bootstrap.servers': 'localhost:9092'}
    producer = Producer(producer_conf)
    topic = 'fila_luminosidade'

    global luminosity

    while True:

        message = f"Luminosidade: {luminosity} lux"
        producer.produce(topic, message.encode('utf-8'))
        producer.flush()
        time.sleep(5)

publish_luminosity_data()
