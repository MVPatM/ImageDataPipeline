# ImageDataPipeline
1. I assume that clients generate the images and send to near flask server.
2. Flask server send images that are sent from many clients to kafka cluster.
   Flask have the role of producer.
3. Consumer bring the images from kafka cluster and augment the images.
   In this case, i just use crop operation to augment four images from a single image. 


![Image](https://github.com/user-attachments/assets/e4a5b7c5-5547-4790-8af9-fb1bed210020)

1. Build data pipeline for image datas
   1) Use exactly-once semantics in kafka
      
   2) Image data is high-volume data. After spilting images, send the pieces of image to kafka.  

   3) I use avro for serialization and deserialization for sending data to kafka cluster

2. To find the suitable size of piece, i tested by varying the size.
   The test was conducted under the circumstance that there was 3 brokers with 3 partitions on 3 servers. 

![Image](https://github.com/user-attachments/assets/abc56d62-dbdb-4fd6-8d62-80d2d484a288)




### Image size
![Image](https://github.com/user-attachments/assets/cc606d93-56d8-4bae-8fb5-56bac9cfe0cf)
