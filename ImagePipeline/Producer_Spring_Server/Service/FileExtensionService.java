package com.example.FileUpload.Service;

import org.apache.tika.Tika;
import org.apache.tika.mime.MimeType;
import org.apache.tika.mime.MimeTypes;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
@RequiredArgsConstructor
public class FileExtensionService {
    private final Tika tika;

    public String getExtension(MultipartFile file) {
        try {
            String mimeType = tika.detect(file.getInputStream());
            MimeTypes allTypes = MimeTypes.getDefaultMimeTypes();
            MimeType type = allTypes.forName(mimeType);
            log.info("File extension: {}", type.getExtension());

            return type.getExtension(); 
        } catch (Exception e) {
            log.error("Failed to detect file extension", e.getMessage(), e);
            throw new RuntimeException("Failed to detect file extension", e);
        }
    }
}
