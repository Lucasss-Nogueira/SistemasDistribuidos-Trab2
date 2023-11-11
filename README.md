# SistemasDistribuidos-Trab2

Foi definido um ambiente de casa inteligente, composto por um home_assistant, três equipamentos (cada um está relacionado a um sensor e um atuador): um AC (sensor contínuo de temperatura), uma lâmpada (sensor de luminosidade) e uma fechadura eletrônica (sensor que retorna se esta aberto ou fechado), tais dispostivios foram definidos de forma abstrata por meio de software.

### Funcionamento da aplicação:

#### 1. Comunicação cliente e Home Assistant

O cliente inicia a interação informando qual equipamento deseja controlar. Em seguida, ele escolhe entre duas opções: obter o estado atual do equipamento ou alterar esse estado. A comunicação entre o cliente e o servidor Home Assistant ocorre por meio de gRPC. O cliente estabelece uma conexão e invoca métodos remotos oferecidos pelo Home Assistant Service, conforme definido no arquivo home_assistant.proto.

- Obter Valor Atual: Se o cliente escolher obter o valor atual do dispositivo, ele receberá a resposta da invocação do método GetSensorData(). Essa resposta contém informações como a luminosidade, temperatura e estado da fechadura.

- Alterar Estado: Se o cliente optar por alterar o estado do equipamento, a resposta será gerada pela invocação do método ControlActuators(). O cliente fornece um objeto ActuatorCommand contendo detalhes sobre a operação desejada, como a temperatura desejada para o AC.

#### 2. Comunicação Home Assistant e sensores

O Home Assistant atua como consumidor para receber e armazenar os estados dos sensores. Ele se inscreve em filas específicas no Apache Kafka, uma para cada tipo de sensor. Os sensores operam como produtores, enviando periodicamente dados para suas respectivas filas. O Kafka notifica o Home Assistant sobre novas mensagens, permitindo que ele colete e armazene essas informações. Quando o cliente solicita o método GetSensorData(), o Home Assistant retorna as informações armazenadas.

#### 3. Comunicação Home Assistant e atuadores

Para que o Home Assistant possa alterar os estados dos sensores a partir da requisição vinda do cliente, ele se comunica com os atuadores a partir do grpc, de forma que o Home Assiant atua como cliente e os atuadores atuam como servidores.

- Considerando o exemplo de o cliente requisitar a alteração de temperatura, ele envia uma solicitação ao Home Assistant através do método ControlActuators() e internamente, o Home Assistant chama a função alterar_temperatura(nova_temperatura), que utiliza o serviço gRPC para se comunicar com o atuador de temperatura (TemperatureActuatorService).

- O atuador de temperatura recebe o comando e realiza as operações necessárias para ajustar a temperatura do sensor, o qual na proxima publicação ao Kafka irá enviar a medição atualizada.
  Esse processo é replicado para outros equipamentos (Locker, Luminosidade) conforme necessário, mantendo a consistência entre o Home Assistant e os atuadores distribuídos na arquitetura do sistema.

### Definição dos protocolos de comunicação via Protocol Buffers:

#### ActuatorCommand -

Utilizado para enviar os comandos.

- equipment - Informa o equipamento ao qual o commando será enviado.
- novo_nivel_luminosidade - Informa o novo valor de estado da lâmpada.
- lock - Informa o novo valor de estado da fechadura.
- Temperatura - Informa o novo valor de temperatura do AC.

#### SensorData -

Utilizado para registrar as ultimas medidas dos sensores pelo Home Assistant.

- luminosity - Última leitura do sensor de luminosidade.
- temperature - Última leitura do sensor de luminosidade.
- is_locked - Ultima leitura do sensor de fechadura.

#### TemperatureActuatorService -

Serviço gRPC para a temperatura

- alterarTemperatura - Este método permite que o Home Assistant envie um comando para alterar a temperatura. Ele recebe um objeto ActuatorCommand como entrada, que incluirá a nova temperatura a ser definida. A operação retorna um objeto google.protobuf.Empty como confirmação de que a operação foi concluída.

#### LuminosityActuatorService -

Serviço gRPC para a luminosidade

- alterarLuminosidade - Esta operação permite que o Home Assistant envie um comando para alterar a luminosidade. Ela também recebe um objeto ActuatorCommand como entrada, que incluirá o novo nível de luminosidade a ser definido. A operação retorna um objeto google.protobuf.Empty como confirmação.

#### LockActuatorService -

Serviço gRPC para a fechadura

- alterarFechadura - Lida com a fechadura, permitindo que o Home Assistant envie comandos para trancar ou destrancar a fechadura. O método recebe um objeto ActuatorCommand como entrada, e a operação retorna um objeto google.protobuf.Empty.

#### HomeAssistantService -

Serviço gRPC para o Home Assistant

- GetSensorData - Esta operação é responsável por obter os dados dos sensores. O Home Assistant pode chamar este método para receber informações sobre o ambiente, como luminosidade, temperatura e estado da fechadura. Retorna um objeto SensorData.
- ControlActuators - Permite que o Home Assistant envie comandos para controlar os atuadores (como temperatura, luminosidade, e fechadura). Recebe um objeto ActuatorCommand e retorna um objeto google.protobuf.Empty como confirmação.

### Linguagens utilizadas:

#### Python

#### Protocol Buffers3

### Bibliotecas utilizadas :

#### grpc

#### Threading

#### Struct

#### Timer

#### Text

#### text_format from google.protobuf

#### Consumer, KafkaError from confluent_kafka

#### futures from concurrent

### Frameworks e Ferramentas Utilizadas:

#### gRPC

- Uso no projeto: comunicação entre o Home Assistant com os atuadores e também do client com o Home Assistant, seguindo o paradigma Cliente/Servidor.

#### Confluent Kafka:

- Uso no projeto: comunicação assíncrona entre os sensores e o Home Assistant, permitindo o envio e recebimento de dados em tempo real através de tópicos específicos.

#### Docker:

- Uso no projeto: criar contêineres isolados para o serviço Kafka, simplificando a configuração e garantindo uma execução consistente.

### Como executar a aplicação:

#### 1. Configuração do Ambiente Kafka

- Crie uma rede Docker para os serviços Kafka:
  ```
  docker network create app-tier --driver bridge
  ```
- Execute o servidor Kafka no contêiner:

  ```
  docker run --rm --name kafka-server --hostname kafka-server \
  --network app-tier \
  -p 9094:9094 \
  -e KAFKA_CFG_NODE_ID=0 \
  -e KAFKA_CFG_PROCESS_ROLES=controller,broker \
  -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093,EXTERNAL://:9094 \
  -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka-server:9092,EXTERNAL://localhost:9094 \
  -e KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,EXTERNAL:PLAINTEXT,PLAINTEXT:PLAINTEXT \
  -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka-server:9093 \
  -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  bitnami/kafka:latest

  ```

#### 2. Execução dos Sensores e Atuadores:

- Em terminais separados, execute os scripts Python correspondentes a cada equipamento:

  - Sensor e Atuador de Temperatura:

    ```
    python temperature.py
    ```

  - Sensor e Atuador de Luminosidade:

    ```
    python luminosity.py
    ```

  - Sensor e Atuador de Fechadura Eletrônica:
    ```
    python locker.py
    ```

#### 3. Execução do Home Assistant:

- Execute o Home Assistant:
  ```
  python home_assistant.py
  ```

#### 4. Execução da Aplicação Cliente:

- Execute a aplicação cliente:
  ```
  python client.py
  ```
