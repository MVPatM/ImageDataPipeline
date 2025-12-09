# For producer
normal_producer_conf = {
    'bootstrap.servers': ':9092',
    'acks': 'all',
    'enable.idempotence': True, 
    'batch.size': '65536',
    'linger.ms': 10
    }

producer_server_url = ':5000/'

# For consumer
consumer_conf = {
    'bootstrap.servers': ':9092',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    'group.id': 'testGroup'
}

db_url = ""

# For both
schema_registry_url = ':8081'

Topic_Name = 'kafkatest'

image_folder = ''

aws_access_key_id = ''

aws_secret_access_key = ''

bucket_name = 'kafkaimage'
