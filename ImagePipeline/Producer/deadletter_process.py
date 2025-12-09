from confluent_kafka import Producer
from ImagePipeline.Producer.producer_config import normal_producer_conf, db_url
from confluent_kafka.serialization import StringDeserializer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ImagePipeline.Producer.producer_dao import DeadLetterDAO
import os, portalocker
from datetime import datetime

sessionlocal = None
string_deserializer = None

def main():
    producer = Producer(normal_producer_conf)
    
    global string_deserializer
    string_deserializer = StringDeserializer('utf_8')
    
    global sessionlocal
    engine = create_engine(db_url, echo=True)
    sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with sessionlocal() as session:
        dead_letter_dao = DeadLetterDAO(session)
        batches = dead_letter_dao.get_dead_letter()
        
        for i, batch in enumerate(batches):
            for dead_letter in batch:
                producer.produce(topic=dead_letter.topic,
                                key=dead_letter.key,
                                value=dead_letter.value, 
                                callback=delivery_report)
                producer.flush()

def write_log_sync(log_file_name: str, content: str) -> None:
    try:
        with portalocker.Lock(log_file_name, 'a', timeout=5) as file:
            file.write(content)
    except Exception as e:
        print(f"error {e} occurs")

# Callback function for sending the result of request
def delivery_report(err, msg):
    if err is not None:
        console_msg = f"Delivery failed for record {msg.value()} at {datetime.now()}: {err}"
        print(console_msg)
        
        # write failure log
        write_log_sync("failure_log.txt", console_msg + "\n")
    else:
        console_msg = f"Record {msg.value()} successfully produced {msg.topic()} [{msg.partition()}] at offset {msg.offset()} and latency is {msg.latency()}"
        print(console_msg)
        
        # delete dead letter from db
        with sessionlocal() as session:
            dead_letter_dao = DeadLetterDAO(session)
            dead_letter_dao.delete_dead_letter(msg.key())
            
        # remove the tmp file
        tmpfile_path = os.path.dirname(os.path.abspath(__file__)) + '/tmp/' + string_deserializer(msg.key())
        if os.path.exists(tmpfile_path):
            os.remove(tmpfile_path)

if __name__ == "__main__":
    main()
