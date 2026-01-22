package com.example.FileUpload.Service;

import com.example.FileUpload.Repository.DeadLetterRepository;
import com.example.proto.ImageMetaDataProto.ImageMetaData;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.nio.charset.StandardCharsets;
import java.util.concurrent.CompletableFuture;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import com.example.FileUpload.Entity.DeadLetter;

@Slf4j
@Service
@RequiredArgsConstructor
public class ImageMetaDataProducer {
    @Qualifier("MetaKafkaTemplate")
    private final KafkaTemplate<String, byte[]> kafkaTemplate;
    private final DeadLetterRepository deadletterRepository;

    @Value("${kafka.topic.image-metadata}")
    private String topic;

    public CompletableFuture<SendResult<String, byte[]>> sendImageMetaDataAsync(String key, String s3Url) {
        // Protocol Buffer 메시지 생성
        ImageMetaData imageMetaData = ImageMetaData.newBuilder()
            .setS3Url(s3Url)
            .build();
        
        // to bytes array
        byte[] messageBytes = imageMetaData.toByteArray();
        
        CompletableFuture<SendResult<String, byte[]>> future = kafkaTemplate.send("test1", key, messageBytes);

        future.whenComplete((result, ex) -> {
            if (ex == null) {
                log.info("Message sent successfully: key={}, topic={}, partition={}, offset={}", 
                    key, 
                    result.getRecordMetadata().topic(),
                    result.getRecordMetadata().partition(),
                    result.getRecordMetadata().offset());
            } else {
                log.error("Failed to send message: key={}, error={}", key, ex.getMessage(), ex);
                // 실패한 메시지 DeadLetter 테이블에 저장
                saveToDeadLetter(key.getBytes(StandardCharsets.UTF_8), messageBytes, topic);
            }
        });
        
        return future;
    }   
    
    @Transactional
    protected void saveToDeadLetter(byte[] key, byte[] value, String topic) {
        try {
            DeadLetter deadLetter = DeadLetter.builder()
                    .key(key)
                    .value(value)
                    .topic(topic)
                    .build();
            
            deadletterRepository.save(deadLetter);
            log.info("Message saved to DeadLetter table: topic={}, key={}", topic, new String(key, StandardCharsets.UTF_8));
            
        } catch (Exception e) {
            log.error("Failed to save message to DeadLetter table: key={}, error={}", 
                    new String(key, StandardCharsets.UTF_8), e.getMessage(), e);
        }
    }
}
