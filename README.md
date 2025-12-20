# ImageDataPipeline

### Program Structure



1. I assume that clients generate the images and send to near fastapi server.
2. Fastapi server send images that are sent from many clients to kafka cluster because of the classfication and augmentation of images in consumer server.
3. Consumer bring the images from kafka cluster and augment the images.

