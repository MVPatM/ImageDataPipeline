import time
import os
import sys
from uuid import uuid4
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField, StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from ImagePipeline.Configuration.kafka_config import image_folder, normal_producer_conf, schema_registry_url, segment_size, Topic_Name
from ImagePipeline.Instance.ImageData import ImageDataFactory

# Callback function for sending the result of request
def delivery_report(err, msg) -> None:
    if err is not None:
        console_msg = f"Delivery failed for record {msg.key()}: {err}"
        console_log(console_msg)
    else:
        console_msg = f"Record {msg.key()} successfully produced {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
        console_log(console_msg)

# Log to the console
def console_log(msg: str) -> None:
    global cnt
    print(msg)
    print(f"{cnt} and time is {time.strftime('%c')}")

def send_image() -> None:
    producer = Producer(normal_producer_conf)
    
    with open(f"{os.path.dirname(os.path.abspath(os.path.dirname(__file__)))}/Configuration/ImageData.avsc") as f:
        schema_str = f.read()
            
    schema_registry_conf = {'url': schema_registry_url}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    avro_serializer = AvroSerializer(schema_registry_client, schema_str, ImageDataFactory.ToDict)
    string_serializer = StringSerializer('utf_8')
    image_data_factory = ImageDataFactory()
    
    while True:
        # read images from the directory
        files = os.listdir(image_folder)
        image_files = [f for f in files]
        
        print(f"start time is {time.strftime('%c')}")
        for image_file in image_files:
            image_path = os.path.join(image_folder, image_file)
            
            # get the image file as bytes type
            with open(image_path, 'rb') as f:
               file = f.read()
            
            # make the message for request
            request_data_to_kafka = dict()
            key = str(uuid4()) + str(int(time.time()))
            NumberOfSegment = int((sys.getsizeof(file) / segment_size))

            # Get the number of segments
            if (sys.getsizeof(file) % segment_size) == 0:
                for i in range(0, NumberOfSegment):
                    producer.poll(0.0)
                    
                    # Chunk the image file
                    request_data = image_data_factory.CreateImageData(NumberOfSegment= NumberOfSegment, 
                                                                      SegmentOrder=i, 
                                                                      Image=file[i*segment_size : (i+1)*segment_size])
                    
                    # produce data to kafka cluster
                    producer.produce(topic=Topic_Name, key = string_serializer(key), value= avro_serializer(request_data, SerializationContext(Topic_Name, MessageField.VALUE)), callback=delivery_report)
            else:
                NumberOfSegment += 1
                
                for i in range(0, NumberOfSegment - 1):
                    producer.poll(0.0)
                    
                    # Chunk the image file
                    request_data = image_data_factory.CreateImageData(NumberOfSegment=NumberOfSegment, 
                                                                      SegmentOrder=i, 
                                                                      Image=file[i*segment_size : (i+1)*segment_size])
                    
                    # produce data to kafka cluster
                    producer.produce(topic=Topic_Name, key = string_serializer(key), value= avro_serializer(request_data, SerializationContext(Topic_Name, MessageField.VALUE)), callback=delivery_report)
                
                # the last segment that does not fit to segment size because segment is smaller
                producer.poll(0.0)
                request_data = image_data_factory.CreateImageData(NumberOfSegment=NumberOfSegment, 
                                                                  SegmentOrder=NumberOfSegment - 1, 
                                                                  Image=file[(NumberOfSegment - 1)*segment_size:])
                producer.produce(topic=Topic_Name,key = string_serializer(key) ,value= avro_serializer(request_data, SerializationContext(Topic_Name, MessageField.VALUE)), callback=delivery_report)
                
            producer.flush()
        break

if __name__ == "__main__":
    send_image()
