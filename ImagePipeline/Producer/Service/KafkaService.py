from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from ImagePipeline.Configuration import ImageData_pb2 as imagedata_pb2
from ImagePipeline.Configuration import ImageMetaData_pb2 as imagemetadata_pb2
from confluent_kafka.serialization import StringDeserializer, StringSerializer
import os
from time import time
from dotenv import load_dotenv

class KafkaService:
    def __init__(self):
        load_dotenv()
        
        schema_registry_url = os.getenv('SCHEMA_REGISTRY_URL')

        schema_registry_conf = {'url': schema_registry_url}
        self._schema_registry_client = SchemaRegistryClient(schema_registry_conf)
        self._string_serializer = StringSerializer('utf_8')
        self._string_deserializer = StringDeserializer('utf_8')
    
    def produceDeadLetter(self, topic: str, key: bytes, value: bytes, delivery_report):
        self._producer.produce(topic, key, value, delivery_report)
        self._producer.poll(0)
    
    def get_string_deserializer(self) -> StringDeserializer:
        return self._string_deserializer
    
    def msg_flush(self):
        self._producer.flush()
    
class KafkaMetaService(KafkaService):
    def __init__(self):
        super().__init__()
        
        self.topic_name_meta = os.getenv('TOPIC_NAME_META')

        normal_producer_conf = {
            "bootstrap.servers": "ec2-3-38-42-211.ap-northeast-2.compute.amazonaws.com:9092",  
            "acks": "all",  
            "enable.idempotence": True, 
            "batch.size": 1024, # 1kb
            "linger.ms": 10}
        
        self._producer = Producer(normal_producer_conf)
        self._serializer_meta = ProtobufSerializer(imagemetadata_pb2.ImageMetaData,
                                            self._schema_registry_client,
                                            {'use.deprecated.format': False})
        self._serializer_payload = ProtobufSerializer(imagedata_pb2.ImageData,
                                            self._schema_registry_client,
                                            {'use.deprecated.format': False})
        self._string_serializer = StringSerializer('utf_8')
        self._string_deserializer = StringDeserializer('utf_8')
    
    def produceMetaData(self, s3_url: str, file_fullname: str, delivery_report) -> None:
        request_data_to_kafka = imagemetadata_pb2.ImageMetaData(s3_url=s3_url, 
                                                                produce_time=int(time.time() * 1000))
        self._producer.produce(topic=self.topic_name_meta,
                           key=self._string_serializer(file_fullname),
                           value=self._serializer_meta(request_data_to_kafka,
                                            SerializationContext(self.topic_name_meta, MessageField.VALUE)), 
                           callback=delivery_report)
        self._producer.poll(0)

class KafkaPayloadService(KafkaService):
    def __init__(self):
        super().__init__()
        
        self.topic_name_payload = os.getenv('TOPIC_NAME_PAYLOAD')
       
        normal_producer_conf = {
            "bootstrap.servers": "ec2-3-38-42-211.ap-northeast-2.compute.amazonaws.com:9092",  
            "acks": "all",  
            "enable.idempotence": True, 
            "batch.size": 131072, # 128kb    
            "linger.ms": 10}
        
        self._producer = Producer(normal_producer_conf)
        self._serializer_meta = ProtobufSerializer(imagemetadata_pb2.ImageMetaData,
                                            self._schema_registry_client,
                                            {'use.deprecated.format': False})
        self._serializer_payload = ProtobufSerializer(imagedata_pb2.ImageData,
                                            self._schema_registry_client,
                                            {'use.deprecated.format': False})
        self._string_serializer = StringSerializer('utf_8')
        self._string_deserializer = StringDeserializer('utf_8')
    
    def producePayload(self, file_fullname: str, imagedata: bytes, delivery_report) -> None:
        request_data_to_kafka = imagedata_pb2.ImageData(Image=imagedata,
                                                    produce_time=int(time.time() * 1000))
        
        self._producer.produce(topic=self.topic_name_payload,
                           key=self._string_serializer(file_fullname),
                           value=self._serializer_payload(request_data_to_kafka,
                                            SerializationContext(self.topic_name_payload, MessageField.VALUE)), 
                           callback=delivery_report)
        self._producer.poll(0)
