from ImagePipeline.Producer.Service.KafkaService import KafkaService
from ImagePipeline.Producer.utils.db_utils import get_db_session
from ImagePipeline.Producer.CRUD.producer_dao import DeadLetterDAO
import os
from datetime import datetime

sessionlocal = None
string_deserializer = None

def main():
    kafka_producer = KafkaService()
    
    global string_deserializer
    string_deserializer = kafka_producer.get_string_deserializer()
    
    with get_db_session() as session:
        dead_letter_dao = DeadLetterDAO(session)
        batches = dead_letter_dao.get_dead_letter()
        
        for i, batch in enumerate(batches):
            for dead_letter in batch:
                kafka_producer.produceDeadLetter(dead_letter.topic,
                                                 dead_letter.key,
                                                 dead_letter.value,
                                                 delivery_report)

# Callback function for sending the result of request
def delivery_report(err, msg):
    if err is not None:
        console_msg = f"Delivery failed for record {msg.value()} at {datetime.now()}: {err}"
        print(console_msg)
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
