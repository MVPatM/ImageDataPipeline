from fastapi import FastAPI, File, Depends
from contextlib import asynccontextmanager
from ImagePipeline.Producer.Service.KafkaService import KafkaService
from ImagePipeline.Producer.utils.log import write_log
from ImagePipeline.Producer.utils.FileData import FileData
from ImagePipeline.Producer.CRUD.producer_dao import DeadLetterDAO
import os, sys
from uuid import uuid4
from datetime import datetime
from ImagePipeline.Producer.utils.db_utils import get_db_session
from dotenv import load_dotenv
from aiobotocore.session import get_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    app.state.bucket_name = os.getenv('BUCKET_NAME')
    app.state.kafka_producer = KafkaService()
    
    # async
    async with get_session().create_client('s3', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key) as client:
        app.state.s3_client = client
        yield

    app.state.kafka_producer.msg_flush()
    print("server is exited")

app = FastAPI(lifespan=lifespan)

# Dependency injector 
def get_kafka_producer():
    return app.state.kafka_producer

def get_s3_client():
    return app.state.s3_client

def get_uuid_key() -> str:
    return str(uuid4())

def delivery_report(err, msg):
        if err is not None:
            console_msg = f"Delivery failed for record {msg.value()} at {datetime.now()}: {err}"
            print(console_msg)
            
            # insert dead letter to db
            with get_db_session() as session:
                dao = DeadLetterDAO(session)
                dao.add_dead_letter(msg.key(), msg.value(), msg.topic())
        else:
            console_msg = f"Record {msg.value()} successfully produced {msg.topic()} [{msg.partition()}] at offset {msg.offset()} and latency is {msg.latency()}"
            print(console_msg)
            
            # remove the tmp file
            tmpfile_path = os.path.dirname(os.path.abspath(__file__)) 
            + '/tmp/' 
            + app.state.kafka_producer.get_string_deserializer()(msg.key())
            
            if os.path.exists(tmpfile_path):
                os.remove(tmpfile_path)

# send metadata with s3 url to kafka
async def produce_metadata(file_data: FileData, 
                kafka_producer: KafkaService,
                s3_client) -> None:
    file_fullname = file_data.get_file_fullname()
    s3_url = f'test/{file_fullname}'
    await s3_client.put_object(Body=file_data.get_imgBytesIO(), 
                               Bucket=app.state.bucket_name, 
                               Key=s3_url)
    kafka_producer.produceMetaData(s3_url, file_fullname, delivery_report)

# send payload image directly to kafka
async def produce_img(file_data: FileData,
                kafka_producer: KafkaService) -> None:
    kafka_producer.producePayload(file_data.get_filename() + "." + file_data.get_fileformat() 
                                , file_data.get_imgbyte(), delivery_report)

@app.post("/upload")
async def Middleware(file: bytes = File(),
            file_name = Depends(get_uuid_key),
            kafka_producer = Depends(get_kafka_producer),
            s3_client = Depends(get_s3_client)):
    try:
        file_size = sys.getsizeof(file)
        file_data = FileData(img_byte=file,
                             file_name=file_name)
        
        if file_size > 100 * 1024:  # 100kb
            await produce_metadata(file_data, kafka_producer, s3_client)
        else:
            await file_data.store_tmp()
            await produce_img(file_data, kafka_producer)
        return ({'message': f"success"})
    except Exception as e:
        await write_log("failure_log.txt", f"{e} is occured\n")
        return({'message': f"{e} is occured"})
        
