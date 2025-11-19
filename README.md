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
├── docker-compose.yml
└── setup.sh
```



## Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados:
* [Docker-Desktop](https://www.docker.com/products/docker-desktop/)

## Executando o Projeto

### 1. Iniciar os Containers

No primeiro terminal, inicie os containers com o comando:

```bash
docker-compose up
```
### 2. Aguarde a Configuração Automática
Você verá logs do LocalStack iniciando e, em seguida, um serviço chamado `setup-resources` irá rodar.
Aguarde até aparecer a mensagem:

```bash
setup-resources-1  | === Setup Concluído! ===
setup-resources-1  | URL da API Gateway:
setup-resources-1  | http://localhost:4566/restapis/XXXXXX/prod/_user_request_/pedidos
```

### 3. Copie a URL
Copie a URL exibida no terminal.

## Testando
Com o terminal do Docker rodando (Terminal 1), abra um novo terminal (Terminal 2) para simular o cliente.


### 1. Fazer um Pedido (POST na API)

No Terminal 2, exporte a URL que você copiou e faça o pedido:

```bash
# Substitua pela URL que apareceu no Terminal 1
export API_URL="http://localhost:4566/restapis/SEU_ID_AQUI/prod/_user_request_/pedidos"

# Envia o pedido via Curl
curl -X POST $API_URL \
-H "Content-Type: application/json" \
-d '{
    "cliente": "Maria",
    "itens": ["Moqueca", "Suco de Caju"],
    "mesa": 12
}'
```

**Resposta Esperada:**
```json
{"message": "Pedido criado com sucesso!", "order_id": "..."}
```

### 2. Verificar o Processamento (Logs em Tempo Real)

Imediatamente após fazer o pedido, olhe para o Terminal 1 (onde o Docker está rodando).
Você verá a notificação do SNS aparecer nos logs, confirmando que todo o fluxo (API -> Dynamo -> SQS -> Lambda -> S3 -> SNS) funcionou:
```bash
########################################
      [SNS] NOTIFICAÇÃO ENVIADA      
########################################
=== PEDIDO PRONTO ===
ID: ...
Cliente: Maria
Mesa: 12
Itens: Moqueca, Suco de Caju
=====================
########################################
```
**Resultado Esperado:**
Procure o pedido da "Maria". O `status` dele deve ser **"CONCLUIDO"**.

**Verifique o Comprovante no S3:**
```bash
# Lista os arquivos no bucket de comprovantes
awslocal s3 ls s3://pedidos-comprovantes
```
**Resultado Esperado:**
Você deve ver um arquivo `.txt` com o ID do pedido que acabou de ser criado (ex: `comprovante-....txt`).

## Parando o Projeto
Para desligar e limpar tudo:
```bash
docker-compose down
```
