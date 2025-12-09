from ImagePipeline.Consumer.consumer_db_model import ImageData

class ImageDataDAO:
    def __init__(self, session):
        self.session = session
        
    def add_image_data(self, s3_url: str, image_class: str) -> None:
        data = ImageData(s3_url=s3_url, image_class=image_class)
        self.session.add(data)
        self.session.commit()
