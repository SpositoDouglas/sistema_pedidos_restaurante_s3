import boto3
import json
import os
import sys
import time

ENDPOINT = os.getenv('ENDPOINT_URL', 'http://localstack:4566')
REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
TOPIC_ARN = "arn:aws:sns:us-east-1:000000000000:PedidosConcluidos"

sqs = boto3.client('sqs', endpoint_url=ENDPOINT, region_name=REGION)
sns = boto3.client('sns', endpoint_url=ENDPOINT, region_name=REGION)

def setup_assinatura():
    """Cria uma fila temporária e assina no SNS"""
    queue_name = "Debug-SNS-Listener"
    print(f"🛠️ Criando fila de verificação: {queue_name}...")
    
    try:
        queue = sqs.create_queue(QueueName=queue_name)
        queue_url = queue['QueueUrl']
        
        attrs = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['QueueArn'])
        queue_arn = attrs['Attributes']['QueueArn']
    except Exception as e:
        print(f"❌ Erro ao criar fila: {e}")
        sys.exit(1)

    print(f"🔗 Assinando fila ao tópico SNS...")
    try:
        sns.subscribe(
            TopicArn=TOPIC_ARN,
            Protocol='sqs',
            Endpoint=queue_arn
        )
    except Exception as e:
        print(f"❌ Erro ao assinar tópico: {e}")
        sys.exit(1)
        
    return queue_url

def monitorar(queue_url):
    print("\n📻 Ouvindo o SNS 'PedidosConcluidos'...")
    
    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=5
            )
            
            if 'Messages' in response:
                for msg in response['Messages']:
                    body = json.loads(msg['Body'])
                    
                    conteudo_sns = body.get('Message', body)
                    
                    print("\n" + "🔔"*10 + " NOTIFICAÇÃO CAPTURADA " + "🔔"*10)
                    print(conteudo_sns)
                    print("🔔"*31 + "\n")

                    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg['ReceiptHandle'])
            else:
                print(".", end="", flush=True)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoramento encerrado.")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            time.sleep(2)

if __name__ == "__main__":
    url = setup_assinatura()
    monitorar(url)