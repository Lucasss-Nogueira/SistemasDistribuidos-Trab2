from confluent_kafka import Producer
from concurrent.futures import ThreadPoolExecutor
import grpc
import home_assistant_pb2_grpc
import google.protobuf.empty_pb2
import time
import threading

temperature = 25  # Inicia com 25 graus Celsius

class TemperatureActuatorService(home_assistant_pb2_grpc.TemperatureActuatorServiceServicer):
    def alterarTemperatura(self, request, context):

        global temperature 
        temperature = request.temperature
    
        msg = f"Temperatura alterada para {temperature}°C"
        print(msg)
        return google.protobuf.empty_pb2.Empty()

server = grpc.server(thread_pool=ThreadPoolExecutor(max_workers=10))
home_assistant_pb2_grpc.add_TemperatureActuatorServiceServicer_to_server(TemperatureActuatorService(), server)
server.add_insecure_port('[::]:15000')
server.start()  



def publish_temperature_data():
    producer_conf = {'bootstrap.servers': 'localhost:9094'}
    producer = Producer(producer_conf)
    topic = 'fila_temperatura'

    global temperature

    while True:
        print(f"Enviando estado da temperatura {temperature}")
        message = f"Temperatura: {temperature}°C"
        producer.produce(topic, message.encode('utf-8'))
        producer.flush()
        time.sleep(5)

publish_temperature_data_thread = threading.Thread(target=publish_temperature_data)
publish_temperature_data_thread.start()

server.wait_for_termination()
