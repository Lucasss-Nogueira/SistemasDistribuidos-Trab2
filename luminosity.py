from confluent_kafka import Producer
from concurrent.futures import ThreadPoolExecutor
import grpc
import home_assistant_pb2_grpc
import google.protobuf.empty_pb2
import time
import threading

luminosity = 150  # Inicia com o máximo de luminosidade 

class LuminosityActuatorService(home_assistant_pb2_grpc.LuminosityActuatorServiceServicer):
    def alterarLuminosidade(self, request, context):
        global luminosity
        luminosity = request.novo_nivel_luminosidade
    
        msg = f"Luminosidade alterada para {luminosity} lux"
        print(msg)
        return google.protobuf.empty_pb2.Empty()

server = grpc.server(thread_pool=ThreadPoolExecutor(max_workers=10))
home_assistant_pb2_grpc.add_LuminosityActuatorServiceServicer_to_server(LuminosityActuatorService(), server)
server.add_insecure_port('[::]:52054')
server.start()  

def publish_luminosity_data():
    producer_conf = {'bootstrap.servers': 'localhost:9094'}
    producer = Producer(producer_conf)
    topic = 'fila_luminosidade'

    global luminosity

    while True:
        print(f"Enviando estado da luminosidade {luminosity}")
        message = f"Luminosidade: {luminosity} lux"
        producer.produce(topic, message.encode('utf-8'))
        producer.flush()
        time.sleep(5)

publish_luminosity_data_thread = threading.Thread(target=publish_luminosity_data)
publish_luminosity_data_thread.start()


server.wait_for_termination()