import socket
import google.protobuf.empty_pb2
import grpc
import threading
import home_assistant_pb2
import home_assistant_pb2_grpc
from confluent_kafka import Consumer, KafkaError
from concurrent import futures

# Conectar aos atuadores via gRPC:

##Locker
channel_locker = grpc.insecure_channel('localhost:51053')
stub_locker = home_assistant_pb2_grpc.LockActuatorServiceStub(channel_locker)

##Luminosidade
channel_luminosity = grpc.insecure_channel('localhost:52054')
stub_luminosity = home_assistant_pb2_grpc.LuminosityActuatorServiceStub(channel_luminosity)

##Temperatura
channel_temperature = grpc.insecure_channel('localhost:15000')
stub_temperature = home_assistant_pb2_grpc.TemperatureActuatorServiceStub(channel_temperature)


# Sensor data
sensor_data = {
    'luminosity': 0,
    'temperature': 0,
    'lock_status': 'false'
}

# Função para alterar o estado do sensor de temperatura
def alterar_temperatura(nova_temperatura):
# global sensor_data
# nova_temperatura = request.novo_nivel_luminosidade
#
    command = home_assistant_pb2.ActuatorCommand(temperature = nova_temperatura, equipment="temperature")
    stub_temperature.alterarTemperatura(command)


# Função para alterar o estado do sensor de fechadura
def alterar_fechadura(novo_estado):
    
    command = home_assistant_pb2.ActuatorCommand(lock = novo_estado, equipment="lock")
    stub_locker.alterarFechadura(command)


def alterar_luminosidade(nova_luminosidade):

    command = home_assistant_pb2.ActuatorCommand(novo_nivel_luminosidade = nova_luminosidade, equipment="luminosity")
    stub_luminosity.alterarLuminosidade(command)


def kafka_consumer():
    conf = {
        'bootstrap.servers': 'localhost:9094',
        'group.id': 'home-assistant-group',
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(conf)
    topics = ['fila_luminosidade', 'fila_temperatura', 'fila_fechadura']
    consumer.subscribe(topics)

    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        message = msg.value().decode('utf-8')
        if 'Luminosidade' in message:
            sensor_data['luminosity'] = int(message.split(': ')[1].split(' ')[0])
            print(f"Luminosidade atual: {sensor_data['luminosity']}")
        elif 'Temperatura' in message:
            sensor_data['temperature'] = int(message.split(': ')[1].split('°C')[0])
            print(f"Temperatura atual: {sensor_data['temperature']}")
        elif 'Fechadura' in message:
            sensor_data['lock_status'] = message.split(': ')[1]
            print(f"Estado da fechadura: {sensor_data['lock_status']}")

kafka_consumer_thread = threading.Thread(target=kafka_consumer)
kafka_consumer_thread.start()

class HomeAssistantService(home_assistant_pb2_grpc.HomeAssistantServiceServicer):
    def GetSensorData(self, request, context):
        return home_assistant_pb2.SensorData(
            luminosity=f"Luminosidade: {sensor_data['luminosity']} lux",
            temperature=f"Temperatura: {sensor_data['temperature']}°C",
            is_locked=True if sensor_data['lock_status'] == 'True' else False
        )

    def ControlActuators(self, request, context):
        global sensor_data
        print(f"Requisição \n{request}")
        if (request.equipment == 'temperature'):
            alterar_temperatura(request.temperature)
            print(f"Valor da temperatura para ser alterado {request.temperature}")
        elif (request.equipment =='lock'):
            alterar_fechadura(request.lock)
        elif (request.equipment == 'luminosity'):
            alterar_luminosidade(request.novo_nivel_luminosidade)

        msg = "Comando realizado com sucesso!!\n\n"
        print(msg)
        return google.protobuf.empty_pb2.Empty()


server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=10))
home_assistant_pb2_grpc.add_HomeAssistantServiceServicer_to_server(HomeAssistantService(), server)
server.add_insecure_port('[::]:50051')
server.start()
server.wait_for_termination()


## Parte TCP (Não sendo utilzada)
# def handle_client(client_socket):
#     while True:
#         data = client_socket.recv(1024).decode('utf-8')
#         if not data:
#             break

#         # Lógica para interagir com o cliente via TCP aqui
#         response = "Resposta para o cliente: " + data
#         client_socket.send(response.encode('utf-8'))

#     client_socket.close()

# tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# tcp_server.bind(('localhost', 12345))
# tcp_server.listen(5)

# while True:
#     client_socket, addr = tcp_server.accept()
#     client_handler = threading.Thread(target=handle_client, args=(client_socket,))
#     client_handler.start()