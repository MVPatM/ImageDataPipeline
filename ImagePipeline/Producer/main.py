from fastapi import FastAPI, File, Depends
from contextlib import asynccontextmanager
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField, Serializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from ImagePipeline.Producer.producer_config import normal_producer_conf, schema_registry_url, Topic_Name_meta, Topic_Name_payload, bucket_name, aws_access_key_id, aws_secret_access_key, db_url
from ImagePipeline.Configuration import ImageData_pb2 as imagedata_pb2
from ImagePipeline.Configuration import ImageMetaData_pb2 as imagemetadata_pb2
import time, os, asyncio, aiofiles, sys
from uuid import uuid4
from datetime import datetime
from ImagePipeline.Producer.FileData import FileData
import portalocker
from confluent_kafka.serialization import StringDeserializer, StringSerializer
from ImagePipeline.Producer.producer_dao import DeadLetterDAO
from aiobotocore.session import get_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    app.state.producer = Producer(normal_producer_conf)
    schema_registry_conf = {'url': schema_registry_url}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    app.state.serializer_meta = ProtobufSerializer(imagemetadata_pb2.ImageMetaData,
                                            schema_registry_client,
                                            {'use.deprecated.format': False})
    app.state.serializer_payload = ProtobufSerializer(imagedata_pb2.ImageData,
                                            schema_registry_client,
                                            {'use.deprecated.format': False})
    app.state.string_serializer = StringSerializer('utf_8')
    app.state.string_deserializer = StringDeserializer('utf_8')
    
    # async
    async with get_session().create_client('s3', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key) as client:
        app.state.s3_client = client
   
    # db config
    engine = create_engine(db_url, echo=True)
    app.state.sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield 
    print("server is exited")

app = FastAPI(lifespan=lifespan)

# Dependency injector 
def get_producer() -> any:
    return app.state.producer

def get_serializer_meta() -> Serializer:
    return app.state.serializer_meta

def get_serializer_payload() -> Serializer:
    return app.state.serializer_payload

def get_s3_client():
    return app.state.s3_client

def get_uuid_key() -> str:
    return str(uuid4())

def get_string_serializer():
    return app.state.string_serializer

def get_string_deserializer():
    return app.state.string_deserializer

@contextmanager
def get_db_session():
    db = app.state.sessionlocal()
    try:
        yield db
    finally:
        db.close()

# send metadata with s3 url to kafka
async def delivery_file(file_data: FileData, 
                kafka_producer: Producer,
                serializer: Serializer,
                string_serializer: StringSerializer,
                s3_client) -> None:
    file_fullname = file_data.get_file_fullname()
    s3_url = f'test/{file_fullname}'
    await s3_client.put_object(Body=file_data.get_imgBytesIO(), Bucket=bucket_name, Key=s3_url)
    
    request_data_to_kafka = imagemetadata_pb2.ImageMetaData(s3_url=s3_url, produce_time=int(time.time() * 1000))
    kafka_producer.produce(topic=Topic_Name_meta,
                           key=string_serializer(file_fullname),
                           value=serializer(request_data_to_kafka,
                                            SerializationContext(Topic_Name_meta, MessageField.VALUE)), 
                           callback=delivery_report)
    kafka_producer.poll(0)

# send payload image directly to kafka
async def produce_img(file_data: FileData,
                kafka_producer: Producer,
                serializer: Serializer,
                string_serializer: StringSerializer) -> None:
    file_fullname = file_data.get_filename() + "." + file_data.get_fileformat()
    request_data_to_kafka = imagedata_pb2.ImageData(Image=file_data.get_imgbyte(),
                                                    produce_time=int(time.time() * 1000))
    kafka_producer.produce(topic=Topic_Name_payload,
                           key=string_serializer(file_fullname),
                           value=serializer(request_data_to_kafka,
                                            SerializationContext(Topic_Name_payload, MessageField.VALUE)), 
                           callback=delivery_report)
    kafka_producer.poll(0)

# write log function
def write_log_sync(log_file_name: str, content: str) -> None:
    try:
        with portalocker.Lock(log_file_name, 'a', timeout=5) as file:
            file.write(content)
    except Exception as e:
        print(f"error {e} occurs")

async def write_log(log_file_name: str, content: str) -> None:
    async with aiofiles.open(log_file_name, 'a') as f:
        while True:
            try:
                portalocker.lock(f._file, portalocker.LOCK_EX | portalocker.LOCK_NB)
                break
            except portalocker.exceptions.LockException:
                await asyncio.sleep(0.1)
        try:
            await f.write(content)
            await f.flush()
        finally:
            portalocker.unlock(f._file)

# Callback function for sending the result of request
def delivery_report(err, msg):
    if err is not None:
        console_msg = f"Delivery failed for record {msg.value()} at {datetime.now()}: {err}"
        print(console_msg)
        
        # insert dead letter to db
        with get_db_session() as session:
            dao = DeadLetterDAO(session)
            dao.add_dead_letter(msg.key(), msg.value(), msg.topic())
        
        # write failure log
        write_log_sync("failure_log.txt", console_msg + "\n")
    else:
        console_msg = f"Record {msg.value()} successfully produced {msg.topic()} [{msg.partition()}] at offset {msg.offset()} and latency is {msg.latency()}"
        print(console_msg)
        
        # remove the tmp file
        tmpfile_path = os.path.dirname(os.path.abspath(__file__)) + '/tmp/' + get_string_deserializer()(msg.key())
        if os.path.exists(tmpfile_path):
            os.remove(tmpfile_path)

# q
@app.post("/upload")
async def Middleware(file: bytes = File(),
            file_name = Depends(get_uuid_key),
            kafka_producer = Depends(get_producer),
            string_serializer = Depends(get_string_serializer),
            s3_client = Depends(get_s3_client)):
    try:
        file_size = sys.getsizeof(file)
        file_data = FileData(img_byte=file,
                             file_name=file_name)
        
        if file_size > 100 * 1024:  # 100kb
            await delivery_file(file_data, kafka_producer, get_serializer_meta(), string_serializer, s3_client)
        else:
            await file_data.store_tmp()
            await produce_img(file_data, kafka_producer, get_serializer_payload(), string_serializer)
        return ({'message': f"success"})
    except Exception as e:
        await write_log("failure_log.txt", f"{e} is occured\n")
        return({'message': f"{e} is occured"})
        
