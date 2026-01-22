package com.example.FileUpload.Controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.example.FileUpload.Service.ImageDataProducer;
import com.example.FileUpload.Service.ImageMetaDataProducer;
import com.example.FileUpload.Service.S3ImageService;
import com.example.FileUpload.Service.FileExtensionService;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;
import java.util.HashMap;
import java.util.UUID;

@Slf4j
@RestController
@RequiredArgsConstructor
public class FileUploadController {
    private final ImageMetaDataProducer metaDataProducer;
    private final ImageDataProducer imageDataProducer;
    private final S3ImageService s3ImageService;
    private final FileExtensionService fileExtensionService;

    private static final long SIZE_THRESHOLD_KB = 200;
    private static final long SIZE_THRESHOLD_BYTES = SIZE_THRESHOLD_KB * 1024;

    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> uploadImage(
            @RequestParam MultipartFile file) {
        try {
            long fileSizeBytes = file.getSize();
            String fileName = UUID.randomUUID().toString();
            String contentType = fileExtensionService.getExtension(file);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("fileName", fileName);
            response.put("type", contentType);

            if (fileSizeBytes >= SIZE_THRESHOLD_BYTES) {
                log.info("Large file detected.");

                byte[] imageData = file.getBytes();
                String s3Url = s3ImageService.uploadImageWithId(imageData, fileName, contentType);
                //metaDataProducer.sendImageMetaDataAsync(fileName, s3Url);

                response.put("message", "Image uploaded to S3 and then metadata sent to Kafka asynchronously");
            } else {
                log.info("Small file detected.");

                //imageDataProducer.sendImageDataAsync(fileName, file.getBytes());
                response.put("message", "Image data sent to Kafka asynchronously");
            }

            return ResponseEntity.ok().body(response);

        } catch (Exception e) {
            log.error("Failed to upload image: error={}", e.getMessage(), e);
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", e.getMessage());
            return ResponseEntity.status(500).body(response);
        }
    }
}
