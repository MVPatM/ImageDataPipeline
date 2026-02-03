package com.example.Post.Service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Retryable;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.presigner.model.GetObjectPresignRequest;
import software.amazon.awssdk.services.s3.presigner.model.PresignedGetObjectRequest;
import java.time.Duration;

import com.example.Post.DTO.FileDataDTO;

@Slf4j
@Service
@RequiredArgsConstructor
public class S3ImageService {
    private final S3Client s3Client;
    private final S3Presigner s3Presigner;

    @Value("${aws.s3.bucket-name}")
    private final String bucketName;

    @Value("${aws.s3.base-path:test}")
    private final String basePath;

    @Value("${aws.s3.retries}")
    private final int retries;

    @Retryable(retryFor = { Exception.class }, maxAttempts = 3, backoff = @Backoff(delay = 1000))
    public void uploadImageWithId(byte[] imageData, FileDataDTO filedata) {
        try {
            String s3_url = getS3url(filedata);

            log.info("Uploading image with ID to S3: bucket={}, key={}, size={} bytes", bucketName, s3_url, imageData.length);

            PutObjectRequest putObjectRequest = PutObjectRequest.builder()
                    .bucket(bucketName)
                    .key(s3_url)
                    .contentType(filedata.mimeType())
                    .contentLength((long) imageData.length)
                    .build();

            s3Client.putObject(putObjectRequest, RequestBody.fromBytes(imageData));
            log.info("Image uploaded successfully: {}", s3_url);
        } catch (Exception e) {
            log.error("Failed to upload image with ID to S3: error={}", e.getMessage(), e);
            throw new RuntimeException("S3 upload failed: " + e.getMessage(), e);
        }
    }

    public String getS3url(FileDataDTO filedata) {
        return String.format("%s/%s%s", basePath, filedata.fileName(), filedata.extensionType());
    }

    public String getPresignedUrl(String s3_url) {
        GetObjectRequest getObjectRequest = GetObjectRequest.builder()
                .bucket(bucketName)
                .key(s3_url)
                .build();

        GetObjectPresignRequest getObjectPresignRequest = GetObjectPresignRequest.builder()
                .signatureDuration(Duration.ofMinutes(10))
                .getObjectRequest(getObjectRequest)
                .build();

        PresignedGetObjectRequest presignedGetObjectRequest = s3Presigner.presignGetObject(getObjectPresignRequest);

        return presignedGetObjectRequest.url().toString();
    }
}
