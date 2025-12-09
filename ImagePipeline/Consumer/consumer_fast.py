from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer
from confluent_kafka.serialization import StringDeserializer
from .consumer_config import consumer_conf, Topic_Name_meta, aws_access_key_id, aws_secret_access_key, bucket_name, db_url
from ImagePipeline.Configuration import ImageMetaData_pb2 as imagemetadata_pb2
import multiprocessing, boto3
from PIL import Image
from io import BytesIO
import numpy as np
import albumentations as A
from transformers import pipeline
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ImagePipeline.Consumer.consumer_dao import ImageDataDAO

def get_image(s3_client, s3_url: str) -> BytesIO:
    buffer = BytesIO()
    s3_client.download_fileobj(bucket_name, s3_url, buffer)
    return buffer
    
def get_class(image: BytesIO) -> str:
    image = Image.open(image) # pillow로 변환
    classifier = pipeline("image-classification", model="google/vit-base-patch16-224")
    result = classifier(image)
    return result[0]['label']

# pillow로 변환 필요함
def image_augment(image: BytesIO) -> BytesIO: 
    np_img = np.array(Image.open(image))
    transform = A.Compose([A.Resize(256, 256)])
    aug_img = transform(image=np_img)["image"]
    
    buffer = BytesIO()
    pil_img = Image.fromarray(aug_img)
    pil_img.save(buffer, format = 'png')
    return buffer

def get_image_from_kafka(s3_client, sessionlocal) -> None:
    deserializer = ProtobufDeserializer(imagemetadata_pb2.ImageMetaData, {'use.deprecated.format': False})
    string_deserializer = StringDeserializer('utf_8')
    
    # subscribe to kafka topic
    consumer = Consumer(consumer_conf)
    consumer.subscribe([Topic_Name_meta])
    
    while True:
        # get the message from the topic and deserialize the message
        msg = consumer.poll(5.0)
        if msg is None:
            print("message is None")
            continue
        
        response_data = deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))

        # get image from s3
        s3_url = response_data.s3_url
        image_bytesIO = get_image(s3_client, s3_url)
        image_class = get_class(image_bytesIO)
        image_bytesIO = image_augment(image_bytesIO)
        
        try:
            # upload the file to s3
            upload_s3_url = "upload_test/" + string_deserializer(msg.key())
            image_bytesIO.seek(0)
            s3_client.upload_fileobj(image_bytesIO, bucket_name, upload_s3_url)
            
            # upload metadata to mysql 
            with sessionlocal() as session:
                dao = ImageDataDAO(session)
                dao.add_image_data(s3_url, image_class)
            
            # Commit the message directly
            consumer.commit(message=msg, asynchronous=False)
        except Exception as e:
            print(f"error {e} occurs")
    
    consumer.close()


def MiddleWare() -> None:
    s3_client = boto3.client('s3',
                             aws_access_key_id = aws_access_key_id,
                             aws_secret_access_key = aws_secret_access_key)
    
    # set to mysql config
    engine = create_engine(db_url, echo=True)
    sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # multiprocessing
    procs = []
    for i in range(3):
        p = multiprocessing.Process(
            target=get_image_from_kafka,
            args=(s3_client, sessionlocal)
        )
        procs.append(p)
        p.start()

    for p in procs:
        p.join()

if __name__ == "__main__":
    MiddleWare()
    
