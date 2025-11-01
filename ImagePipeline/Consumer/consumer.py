from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField, StringDeserializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from ImagePipeline.Configuration.kafka_config import consumer_conf, schema_registry_url, Topic_Name, Clean_Period_ms, aws_access_key_id, aws_secret_access_key, bucket_name, db_server, db_name, collection_name
import numpy as np
import cv2
import os
import time
import boto3
import threading

def get_image_from_kafka(TempStorage: dict, PerStorage: dict, s3_client, collection) -> None:
    with open(f"{os.path.dirname(os.path.abspath(os.path.dirname(__file__)))}/Configuration/ImageData.avsc") as f:
        schema_str = f.read()
    
    schema_registry_conf = {'url': schema_registry_url}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    avro_deserializer = AvroDeserializer(schema_registry_client,
                                         schema_str)
    key_deserializer = StringDeserializer('utf_8')
    
    # subscribe to kafka topic
    consumer = Consumer(consumer_conf)
    consumer.subscribe([Topic_Name])
    
    while True:
        # get the message from the topic and deserialize the message
        msg = consumer.poll(5.0)
        if msg is None:
            print("message is None")
            continue
        
        response_data = avro_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
        name = key_deserializer(msg.key())
        
        # the case of existing the response key
        if name in TempStorage:
            # Check to exist the list for image file because of the faliure before making list for image.
            if 'Image' not in TempStorage[name]:
                print("Not making the list for images")
                nested_dict = {'Image': [None] * response_data['NumberOfSegment']}
                TempStorage[name] = nested_dict
            
            # Check the duplicate input
            if TempStorage[name]['Image'][response_data['SegmentOrder']] != None:
                print("Already store image file")
                consumer.commit(message=msg, asynchronous=False)
                continue
            
            # Store the image segment
            print("Store image to list")
            nested_arr = TempStorage[name]['Image']
            nested_arr[response_data['SegmentOrder']] = response_data['Image']
            nested_dict = {'Image': nested_arr}
            TempStorage[name] = nested_dict
            
        # the case of not existing the response key
        else:
            # Check the duplicate input
            if name in PerStorage:
                consumer.commit(message=msg, asynchronous=False)
                continue
            
            # Generate the dictionary for key and store image segment to list
            print("Make the list")
            nested_dict = {'Image': [None] * response_data['NumberOfSegment'], 'Time': msg.timestamp()}
            nested_dict['Image'][response_data['SegmentOrder']] = response_data['Image']
            TempStorage[name] = nested_dict
            PerStorage[name] = True
            

        # check whether all segments arrives
        if None not in TempStorage[name]['Image']:
            print('Generate the augmented images')
            
            # Merge all segments
            nested_arr = TempStorage[name]['Image']
            Image = nested_arr[0]
            
            for i in range(1, response_data['NumberOfSegment']):
                Image += nested_arr[i]

            # From bytes to numpy array
            arr = np.asarray(bytearray(Image), dtype=np.uint8)
            numpyarr = cv2.imdecode(buf=arr, flags=1)
            
            # Save the temporary image
            ImageName = 'Tmp/' + name + '.JPEG'
            cv2.imwrite(ImageName, numpyarr)
            
            # Upload the file to s3
            filepath = os.path.dirname(os.path.realpath(__file__)) + '/' + ImageName
            upload_url = 'img/' + name + '.JPEG'
            with open(filepath, 'rb') as file_obj:
               s3_client.upload_fileobj(file_obj, bucket_name, upload_url)

            # Upload the file to mongodb
            collection.insert_one({
                "s3_url": upload_url,
                "upload_date": datetime.now()
            })
            
            # Delete the tmp file
            if os.path.exists(filepath):
                os.remove(filepath)
                
            # Delete key and value
            del TempStorage[name]
        
        #Commit the message directly
        consumer.commit(message=msg, asynchronous=False)
    
    consumer.close()

def Clean_Dict(TempStorage: dict) -> None:
    Present_Time = round(time.time() * 1000)
    
    while True:
        for key in list(TempStorage):
            Generated_time = TempStorage[key]['Time']
            
            # Delete the old message
            if (Present_Time - Generated_time) > Clean_Period_ms:
                del TempStorage[key]

        # Iterate every 15 minutes
        time.sleep(900)
    
def MiddleWare() -> None:
    # Define the shared storage
    tempStorage = dict()
    perStorage = dict()
    s3_client = boto3.client('s3',
                             aws_access_key_id = aws_access_key_id,
                             aws_secret_access_key = aws_secret_access_key)

    # Set to MongoDB config
    client = MongoClient(db_server)
    db = client[db_name] 
    collection = db[collection_name]
    
    # multiprocessing
    processes = []
    for i in range(3):
        p = multiprocessing.Process(
            target=get_image_from_kafka,
            args=(tempStorage, perStorage, s3_client, collection,)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
    


if __name__ == "__main__":
    MiddleWare()    
