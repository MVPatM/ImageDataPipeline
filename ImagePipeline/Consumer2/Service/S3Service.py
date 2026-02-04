import boto3
from PIL import Image
import io
from ImagePipeline.Configuration.kafka_config import aws_access_key_id, aws_secret_access_key

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client('s3', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key)

    def get_image_from_s3(self, bucket: str, key: str):
        try:
            print(f"Fetching image from Bucket: {bucket}, Key: {key}")
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            image_data = response['Body'].read()
            return Image.open(io.BytesIO(image_data))
        except Exception as e:
            print(f"Error fetching image from S3: {e}")
            return None
