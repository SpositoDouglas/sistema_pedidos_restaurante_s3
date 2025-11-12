import json
import boto3
import uuid
import os

LOCALSTACK_ENDPOINT = 'http://localstack:4566'


if os.environ.get('AWS_LAMBDA_RUNTIME_API'):

    dynamodb = boto3.resource('dynamodb', endpoint_url=LOCALSTACK_ENDPOINT)
    sqs = boto3.client('sqs', endpoint_url=LOCALSTACK_ENDPOINT)
else:

    dynamodb = boto3.resource('dynamodb')
    sqs = boto3.client('sqs')


TABLE_NAME = "Pedidos"
QUEUE_URL = f"{LOCALSTACK_ENDPOINT}/000000000000/FilaDePedidos"
TABLE = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:

        body = json.loads(event.get('body', '{}'))

        cliente = body.get('cliente')
        itens = body.get('itens')
        mesa = body.get('mesa')

        if not cliente or not itens or not mesa:
            return {'statusCode': 400, 'body': json.dumps('Erro: Faltando cliente, itens ou mesa.')}


        order_id = str(uuid.uuid4())
        item = {
            'id': order_id,
            'cliente': cliente,
            'itens': itens,
            'mesa': mesa,
            'status': 'PENDENTE'
        }


        TABLE.put_item(Item=item)


        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps({'order_id': order_id})
        )


        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Pedido criado com sucesso!', 'order_id': order_id})
        }

    except Exception as e:
        print(f"Erro: {e}")
        return {'statusCode': 500, 'body': json.dumps('Erro interno no servidor.')}