package com.example.FileUpload.Service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.core.sync.RequestBody;

@Slf4j
@Service
@RequiredArgsConstructor
public class S3ImageService {
    private final S3Client s3Client;

    @Value("${aws.s3.bucket-name}")
    private String bucketName;

    @Value("${aws.s3.base-path:test}")
    private String basePath;

    public String uploadImageWithId(byte[] imageData, String fileName, String contentType) {
        try {
            String extension = extractFileExtension(fileName);
            String s3_url = String.format("%s/%s%s", basePath, fileName, extension);

            log.info("Uploading image with ID to S3: bucket={}, key={}, size={} bytes", 
                    bucketName, s3_url, imageData.length);

            PutObjectRequest putObjectRequest = PutObjectRequest.builder()
                    .bucket(bucketName)
                    .key(s3_url)
                    .contentType(contentType)
                    .contentLength((long) imageData.length)
                    .build();

            s3Client.putObject(putObjectRequest, RequestBody.fromBytes(imageData));
            log.info("Image uploaded successfully: {}", s3_url);

            return s3_url;

        } catch (Exception e) {
            log.error("Failed to upload image with ID to S3: error={}", e.getMessage(), e);
            throw new RuntimeException("S3 upload failed: " + e.getMessage(), e);
        }
    }

    private String extractFileExtension(String fileName) {
        if (fileName == null || !fileName.contains(".")) {
            return "";
        }
        return fileName.substring(fileName.lastIndexOf("."));
    }
}
