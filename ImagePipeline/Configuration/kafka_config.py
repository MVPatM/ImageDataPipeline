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

Clean_Period_ms = 15 * 60 * 1000

# For both
schema_registry_url = ':8081'

Topic_Name = 'kafkatest'

image_folder = ''

segment_size = 30000

aws_access_key_id = ''

aws_secret_access_key = ''

bucket_name = 'kafkaimage'
