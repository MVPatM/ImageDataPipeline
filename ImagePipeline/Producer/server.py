from flask import Flask, request, jsonify
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField, StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from ImagePipeline.Configuration.kafka_config import normal_producer_conf, schema_registry_url, segment_size, Topic_Name
import logging
import os
import sys
from uuid import uuid4

app = Flask(__name__) 
producer = Producer(normal_producer_conf)
avro_serializer = None
string_serializer = None

def _setup() -> None:
    # Get the avro schema and registry to server
    global avro_serializer, string_serializer
    
    with open(f"{os.path.dirname(os.path.abspath(os.path.dirname(__file__)))}/Configuration/ImageData.avsc") as f:
        schema_str = f.read()
            
    schema_registry_conf = {'url': schema_registry_url}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    avro_serializer = AvroSerializer(schema_registry_client, schema_str)
    string_serializer = StringSerializer('utf_8')

# Callback function for sending the result of request
def delivery_report(err, msg):
    if err is not None:
        console_msg = f"Delivery failed for record {msg.key()}: {err}"
        console_log(app, console_msg)
    else:
        console_msg = f"Record {msg.key()} successfully produced {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
        console_log(app, console_msg)

# Log to the console
def console_log(app: Flask, msg: str):
    app.logger.setLevel(logging.DEBUG)
    app.logger.info(msg=msg)

@app.route("/", methods=['POST'])
def MiddleWare(): 
    global avro_serializer, string_serializer
    app.logger.setLevel(logging.DEBUG)
    app.logger.info(msg=avro_serializer)
    
    # get data from client
    image_data_file = request.files.get('file')
    image_byte_file = image_data_file.stream.read()
    
    # make the message for request
    request_data_to_kafka = dict()
    key = str(uuid4()) + str(int(time.time()))
    NumberOfSegment = int((sys.getsizeof(image_byte_file) / segment_size))
    
    # Get the number of segments
    if (sys.getsizeof(image_byte_file) % segment_size) == 0:
        for i in range(0, NumberOfSegment):
            producer.poll(0.0)
            
            # Chunk the image file
            request_data_to_kafka['Image'] = image_byte_file[i*segment_size : (i+1)*segment_size]
            request_data_to_kafka['SegmentOrder'] = i
            
            # produce data to kafka cluster
            producer.produce(topic=Topic_Name, key = string_serializer(key), value= avro_serializer(request_data_to_kafka, SerializationContext(Topic_Name, MessageField.VALUE)), callback=delivery_report)
    else:
        NumberOfSegment += 1
        request_data_to_kafka['NumberOfSegment'] = NumberOfSegment
        
        for i in range(0, NumberOfSegment - 1):
            producer.poll(0.0)
            
            # Chunk the image file
            request_data_to_kafka['Image'] = image_byte_file[i*segment_size : (i+1)*segment_size]
            request_data_to_kafka['SegmentOrder'] = i
            
            # produce data to kafka cluster
            producer.produce(topic=Topic_Name, key = string_serializer(key), value= avro_serializer(request_data_to_kafka, SerializationContext(Topic_Name, MessageField.VALUE)), callback=delivery_report)
        
        # the last segment that does not fit to segment size because segment is smaller
        producer.poll(0.0)
        request_data_to_kafka['Image'] = image_byte_file[(NumberOfSegment - 1)*segment_size:]
        request_data_to_kafka['SegmentOrder'] = NumberOfSegment - 1
        producer.produce(topic=Topic_Name,key = string_serializer(key) ,value= avro_serializer(request_data_to_kafka, SerializationContext(Topic_Name, MessageField.VALUE)), callback=delivery_report)
        
    producer.flush()
    
    return jsonify({'message': "success"}), 200
    
if __name__ == "__main__":
    app.before_request(_setup)
    app.run(debug=True)
