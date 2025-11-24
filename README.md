# Sistema de Pedidos Serverless para Restaurante (LocalStack)
Este projeto simula um sistema de gerenciamento de pedidos de restaurante utilizando uma arquitetura serverless completa.
Todo o ambiente é executado 100% localmente usando **Docker** e **LocalStack**.

O fluxo é o seguinte:
1.  Um cliente faz um pedido via API (API Gateway).
2.  O pedido é validado por uma Lambda, que o salva no DynamoDB e envia um ID para uma fila (SQS).
3.  Uma segunda Lambda consome da fila, processa o pedido, gera um comprovante simulado no S3 e envia uma notificação (SNS).
4.  Essa segunda Lambda também atualiza o status do pedido no DynamoDB para "CONCLUIDO".

## Arquitetura da Solução

O projeto implementa o diagrama de arquitetura serverless a seguir:

```bash
sistema_pedidos_restaurante
├── lambda_criar_pedido
│  └── app.py
├── lambda_processar_pedido
│  └── app.py
├── .gitignore
├── criar_pedido.py
├── docker-compose.yml
├── monitorar_sns.py
├── processar_pedidos.py
├── README.md
└── setup.sh
```



## Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados:
* [Docker-Desktop](https://www.docker.com/products/docker-desktop/)

## Executando o Projeto

### 1. Iniciar os Containers

No primeiro terminal, inicie os containers com o comando:

```bash
docker-compose up --build
```
### 2. Aguarde a Configuração Automática
Você verá logs do LocalStack iniciando e, em seguida, um serviço chamado `setup-resources` irá rodar.
Aguarde até aparecer a mensagem:

```bash
setup-resources-1  | === Setup Concluído! ===
setup-resources-1  | URL da API Gateway:
setup-resources-1  | http://localhost:4566/restapis/XXXXXX/prod/_user_request_/pedidos
```

## Testando
Com o terminal do Docker rodando (Terminal 1), abra dois novos terminais (Terminal 2 e 3) para simular o sistema.


### 1. Monitorar Notificações (SNS)

Abra o Terminal 2 e execute:

```bash
docker-compose exec app-cliente python monitorar_sns.py
```
Deixe esse terminal aberto. Ele mostrará o comprovante assim que o pedido for processado.

### 2. Criar um Pedido

Em outro terminal, execute o script para criar um pedido. Ele enviará os dados para a API Gateway, que salvará no banco e colocará na fila de espera.
```bash
docker-compose exec app-cliente python criar_pedido.py
```
Siga as instruções na tela (Nome, Mesa, Itens).

### 3. Processar Pedido
Este comando pega o pedido pendente, gera a nota fiscal no S3 e avisa no SNS.
```bash
docker-compose exec app-cliente python processar_pedidos.py
```
**Resultado Esperado:**
1. O script dirá "✅ Lambda executada com sucesso!".
2. No terminal do Passo 1, a notificação do pedido pronto aparecerá instantaneamente.

## Parando o Projeto
Para desligar e limpar tudo:
```bash
docker-compose down
```
