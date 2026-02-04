import sys
import os
import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create/Configure path to allow importing from parent directory (Config, Model)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from confluent_kafka import Consumer
from consumer_config import consumer_conf, Topic_Name
import json
from AIConsumer.DAO.PostDAO import PostDAO
from AIConsumer.Service.S3Service import S3Service
from AIConsumer.Service.AIService import AIService

# Initialize Services
post_dao = PostDAO()
s3_service = S3Service()
ai_service = AIService()

# Initialize Kafka Consumer
consumer = Consumer(consumer_conf)
consumer.subscribe([Topic_Name])

logging.info("Consumer started (AIConsumer). Waiting for messages...")

try:
    while True:
        msg = consumer.poll(1.0)
        
        if msg is None:
            continue
        
        if msg.error():
            logging.error("Consumer error: {}".format(msg.error()))
            continue

        try:
            # Parse message
            raw_value = msg.value().decode('utf-8')
            print(type(raw_value))
            json_data = json.loads(raw_value)
            json_data = json.loads(json_data['payload']['Body'])
       
            # Extract S3 info
            if 'Records' in json_data and len(json_data['Records']) > 0:
                record = json_data['Records'][0]
                bucket_name = record['s3']['bucket']['name']
                key = record['s3']['object']['key']

                # Check DB Status
                post = post_dao.get_post_by_image_url(key)
                
                if post is None:
                    logging.warning(f"Post not found for key: {key}")
                    continue
                
                if post.status.lower() != 'pending':
                    logging.info(f"Post status is '{post.status}', skipping processing for key: {key}")
                    continue

                logging.info(f"Processing Post (Pending). Key: {key}")

                # Fetch Image
                image = s3_service.get_image_from_s3(bucket_name, key)
                
                if image:
                    # Run Prediction
                    result = ai_service.predict(image)
                    
                    if result:
                        logging.info(f"Prediction Result: {result}")
                        logging.info(f"Verdict: {result['label']} (Confidence: {result['score']:.4f})")
                        
                        label_lower = result['label'].lower()
                        if ('ai' in label_lower or 'fake' in label_lower) and result['score'] > 0.5:
                            logging.info("High confidence of AI generation. Adding tag...")
                            post_dao.add_tag_to_post(post.id, "생성형이미지")
                        elif result['score'] > 0.5 and 'real' not in label_lower:
                             pass

                        # Update Status to Active
                        post_dao.update_post_status(post.id, "Active")

                        logging.info("-" * 30)
            else:
                logging.warning("Received message does not match expected S3 event structure.")

        except Exception as e:
            logging.error(f"Error processing message: {e}")

except KeyboardInterrupt:
    logging.info("Aborted by user")
finally:
    consumer.close()
