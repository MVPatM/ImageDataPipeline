package com.example.Post.Service;

import java.util.UUID;
import java.util.Set;

import org.apache.tika.Tika;
import org.apache.tika.mime.MimeType;
import org.apache.tika.mime.MimeTypes;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import com.example.Post.DTO.FileDataDTO;

@Slf4j
@Service
@RequiredArgsConstructor
public class FileService {
    private final Tika tika;

    private static final Set<String> ALLOWED_TYPES = Set.of(
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/avif",
        "image/gif"
    );

    public FileDataDTO getFileData(MultipartFile file) {
        try {
            String filename = UUID.randomUUID().toString();
            String mimeType = tika.detect(file.getInputStream());

            if (!isAllowedType(mimeType)) {
                throw new RuntimeException("Unsupported file type: " + mimeType);
            }

            MimeTypes allTypes = MimeTypes.getDefaultMimeTypes();
            MimeType type = allTypes.forName(mimeType);

            return new FileDataDTO(
                filename,
                type.getExtension(),
                mimeType
            );
        } catch (Exception e) {
            log.error("Failed to detect file extension", e.getMessage(), e);
            throw new RuntimeException("Failed to detect file extension", e);
        }
    }    

    private boolean isAllowedType(String mimeType) {
        return ALLOWED_TYPES.contains(mimeType);
    }
}
