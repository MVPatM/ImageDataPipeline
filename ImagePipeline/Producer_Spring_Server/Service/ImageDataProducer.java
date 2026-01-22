package com.example.FileUpload.Service;

import java.nio.charset.StandardCharsets;
import java.util.concurrent.CompletableFuture;
import com.google.protobuf.ByteString;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.example.FileUpload.Repository.DeadLetterRepository;
import com.example.proto.ImageDataProto.ImageData;
import com.example.FileUpload.Entity.DeadLetter;

@Slf4j
@Service
@RequiredArgsConstructor
public class ImageDataProducer {
    @Qualifier("PayloadKafkaTemplate")
    private final KafkaTemplate<String, byte[]> kafkaTemplate;
    private final DeadLetterRepository deadletterRepository;

    @Value("${kafka.topic.image-data}")
    private String topic;

    public CompletableFuture<SendResult<String, byte[]>> sendImageDataAsync(String fileName, byte[] imageBytes) {
        // Protocol Buffer 메시지 생성
        ImageData imageData = ImageData.newBuilder()
                .setImage(ByteString.copyFrom(imageBytes))
                .setFileName(fileName)
                .build();
          
        
        // to Byte[]
        String key = fileName;
        byte[] messageBytes = imageData.toByteArray();
        
        CompletableFuture<SendResult<String, byte[]>> future = kafkaTemplate.send("test1", key, messageBytes);

        future.whenComplete((result, ex) -> {
            if (ex == null) {
                log.info("ImageData sent successfully: key={}, fileName={}, topic={}, partition={}, offset={}", 
                    key,
                    fileName,
                    result.getRecordMetadata().topic(),
                    result.getRecordMetadata().partition(),
                    result.getRecordMetadata().offset());
            } 
            else {
                log.error("Failed to send ImageData: key={}, fileName={}, error={}", 
                        key, fileName, ex.getMessage(), ex);
                saveToDeadLetter(key.getBytes(StandardCharsets.UTF_8), messageBytes, topic);
            }
        });
        
        return future;
    }


    // logic에 retry로직 추가하기 
    @Transactional
    protected void saveToDeadLetter(byte[] key, byte[] value, String topic) {
        try {
            DeadLetter deadLetter = DeadLetter.builder()
                    .key(key)
                    .value(value)
                    .topic(topic)
                    .build();
            
            deadletterRepository.save(deadLetter);
            log.info("ImageData saved to DeadLetter table: topic={}, key={}", topic, new String(key, StandardCharsets.UTF_8));
            
        } catch (Exception e) {
            log.error("Failed to save ImageData to DeadLetter table: key={}, error={}", 
                    new String(key, StandardCharsets.UTF_8), e.getMessage(), e);
        }
    }
}
