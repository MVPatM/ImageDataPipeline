from locust import task, TaskSet, between, FastHttpUser
from ImagePipeline.Configuration.kafka_config import image_folder
import os, random

class TestTask(TaskSet):
    def on_start(self):
        self.files = list()
        image_path = image_folder + "/test_image"
        file_names = os.listdir(image_path)
        
        for file_name in file_names:
            img = os.path.join(image_path, file_name)
            with open(img, 'rb') as f:
                self.files.append(f.read())
    
    @task
    def send_file(self):
        selected_file = random.choice(self.files)
        files = {'file': selected_file}
        self.client.post('/test', files=files)
    
    
class FileUploadUser(FastHttpUser):
    host = ''
    wait_time = between(1, 3)
    tasks = [TestTask]
