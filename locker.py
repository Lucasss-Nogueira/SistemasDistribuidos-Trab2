from confluent_kafka import Producer
from concurrent.futures import ThreadPoolExecutor
import grpc
import google.protobuf.empty_pb2
import home_assistant_pb2_grpc
import time
import threading

lock_status = 'false' # Inicia destrancada

# ACTUATOR
class LockActuatorService(home_assistant_pb2_grpc.LockActuatorServiceServicer):
    def alterarFechadura(self, request, context):
        global lock_status
        lock_status = request.lock
        msg = f"Fechadura alterada para {lock_status}"
        print(msg)
        return google.protobuf.empty_pb2.Empty()

server = grpc.server(thread_pool=ThreadPoolExecutor(max_workers=10))
home_assistant_pb2_grpc.add_LockActuatorServiceServicer_to_server(LockActuatorService(), server)
server.add_insecure_port('[::]:51053')
server.start()   

# SENSOR PUBLISH
def publish_lock_status():
    producer_conf = {'bootstrap.servers': 'localhost:9094'}
    producer = Producer(producer_conf)
    topic = 'fila_fechadura'


    global lock_status

    while True:
        print(f"Enviando estado da fechadura {lock_status}")
        message = f"Fechadura: {lock_status}"
        producer.produce(topic, message.encode('utf-8'))
        producer.flush()
        time.sleep(5)

publish_lock_status_thread = threading.Thread(target=publish_lock_status)
publish_lock_status_thread.start()

server.wait_for_termination()
