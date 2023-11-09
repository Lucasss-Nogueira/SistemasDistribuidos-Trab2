from confluent_kafka import Producer
import grpc
import futures
import home_assistant_pb2
import home_assistant_pb2_grpc
import time

lock_status = 'Destrancada' # Inicia destrancada

# ACTUATOR
class LockActuatorService(LockActuatorServiceServicer):
    def alterarFechadura(ActuatorCommand):

        lock_status = ActuatorCommand.lock
    
        return home_assistant_pb2.Empty(message="Comando executado com sucesso.")

server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=10))
home_assistant_pb2_grpc.add_LockActuatorServiceServicer_to_server(LockActuatorService(), server)
server.add_insecure_port('[::]:50053')
server.start()   

# SENSOR PUBLISH
def publish_lock_status():
    producer_conf = {'bootstrap.servers': 'localhost:9092'}
    producer = Producer(producer_conf)
    topic = 'fila_fechadura'


    global lock_status

    while True:

        message = f"Fechadura: {lock_status}"
        producer.produce(topic, message.encode('utf-8'))
        producer.flush()
        time.sleep(5)

publish_lock_status()
