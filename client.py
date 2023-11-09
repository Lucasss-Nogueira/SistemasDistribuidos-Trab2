import grpc
import home_assistant_pb2
import home_assistant_pb2_grpc

def menu_principal():
    print("Bem-vindo ao Cliente Home Assistant!")
    print("Escolha o equipamento:")
    print("1. AC")
    print("2. Locker")
    print("3. Lâmpada")
    choice = input("Digite o número correspondente: ")
    return int(choice)

def controlar_ac(stub):
    print("Escolha uma opção:")
    print("1. Obter temperatura atual")
    print("2. Alterar temperatura")
    choice = input("Digite o número correspondente: ")

    if choice == "1":
        response = stub.GetSensorData(home_assistant_pb2.Empty())
        print(f"Temperatura atual: {response.temperature}")
    elif choice == "2":
        temperatura = float(input("Digite a nova temperatura: "))  # Converter para float
        if 16 <= temperatura <= 27:
            command = home_assistant_pb2.ActuatorCommand(temperature=temperatura, equipment="temperature")
            response = stub.ControlActuators(command)
            print(response.message)
        else:
            print("Temperatura inválida. Deve estar entre 16 e 27 graus.")
    else:
        print("Opção inválida")

def controlar_locker(stub):
    print("Escolha uma opção:")
    print("1. Obter estado da fechadura")
    print("2. Alterar estado da fechadura")
    choice = input("Digite o número correspondente: ")

    if choice == "1":
        response = stub.GetSensorData(home_assistant_pb2.Empty())
        print(f"Estado da fechadura: {response.is_locked}")
    elif choice == "2":
        state = input("Digite o estado da fechadura (True ou False): ")
        if state.lower() in ["true", "false"]:
            command = home_assistant_pb2.ActuatorCommand(lock=state.lower() == "true", equipment="lock")
            response = stub.ControlActuators(command)
            print(response.message)
    else:
        print("Opção inválida")

def controlar_lampada(stub):
    print("Escolha uma opção:")
    print("1. Obter estado de luminosidade da lâmpada")
    print("2. Alterar luminosidade da lâmpada")
    choice = input("Digite o número correspondente: ")

    if choice == "1":
        response = stub.GetSensorData(home_assistant_pb2.Empty())
        print(f"Luminosidade da lâmpada: {response.luminosity}")
    elif choice == "2":
        luminosidade = float(input("Digite a nova luminosidade da lâmpada: "))  # Converter para float
        if 0 <= luminosidade <= 150:
            command = home_assistant_pb2.ActuatorCommand(novo_nivel_luminosidade=luminosidade, equipment="luminosity")
            response = stub.ControlActuators(command)
            print(response.message)
        else:
            print("Luminosidade inválida. Deve estar entre 0 e 150 lux.")
    else:
        print("Opção inválida")

def main():
    channel = grpc.insecure_channel('localhost:50051')
    stub = home_assistant_pb2_grpc.HomeAssistantServiceStub(channel)

    while True:
        escolha_equipamento = menu_principal()

        if escolha_equipamento == 1:
            controlar_ac(stub)
        elif escolha_equipamento == 2:
            controlar_locker(stub)
        elif escolha_equipamento == 3:
            controlar_lampada(stub)
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

if __name__ == "__main__":
    main()
