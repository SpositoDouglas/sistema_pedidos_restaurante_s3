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
* [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
* `zip` (para empacotar as Lambdas. No WSL/Ubuntu: `sudo apt install zip`)

## Executando o Projeto

### 1. Iniciar o Ambiente LocalStack

Na raiz do projeto, suba os containers do Docker.

```bash
docker-compose up -d
```
### 2. Criar a Infraestrutura AWS (Local)

```bash
# Torna o script executável (só precisa fazer uma vez)
chmod +x setup.sh

# Executa o script para criar a infraestrutura
./setup.sh
```
O script `setup.sh` irá criar todos os recursos e, ao final, **imprimirá a URL da API Gateway** que usaremos.

## Testando

Após o `setup.sh` rodar com sucesso, podemos fazer um teste de ponta a ponta.

### 1. Fazer um Pedido (POST na API)

Copie a URL da API que apareceu no final do passo anterior e exporte-a como uma variável de ambiente:

```bash
export API_URL="http://localhost:4566/restapis/SEU_API_ID/prod/_user_request_/pedidos"
```

Agora, envie um pedido de teste usando `curl`:

```bash
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

### 2. Verificar o Processamento (DynamoDB e S3)

O `curl` confirma que a **Lambda 1** funcionou. Agora, vamos verificar se a **Lambda 2** (que é assíncrona) também funcionou.

**Verifique o Status no DynamoDB:**
(Dê uns 2-3 segundos para o SQS acionar a Lambda 2)

```bash
# Define o alias para facilitar os comandos
alias awslocal="aws --endpoint-url=http://localhost:4566 --region us-east-1"

# Verifica a tabela de Pedidos
awslocal dynamodb scan --table-name Pedidos
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