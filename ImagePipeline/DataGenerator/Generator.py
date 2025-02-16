import requests
import time
import os
from ImagePipeline.Configuration.kafka_config import producer_server_url, image_folder

def send_image() -> None:
    while True:
        # read images from the directory
        files = os.listdir(image_folder)
        image_files = [f for f in files]
        
        for image_file in image_files:
            image_path = os.path.join(image_folder, image_file)
            
            # get the image file as bytes type
            with open(image_path, 'rb') as f:
               file = f.read()
            
            # prepare for sending and send data to flask server
            files = {"file": file}
            response = requests.post(producer_server_url, files=files)
            print(response)
            
            # wait for a moment
            time.sleep(0.1)

if __name__ == "__main__":
    send_image()