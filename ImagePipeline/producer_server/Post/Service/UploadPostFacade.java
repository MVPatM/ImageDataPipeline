package com.example.Post.Service;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import com.example.Post.DTO.FileDataDTO;
import com.example.Post.DTO.UploadRequest;

@Service
@Slf4j
@RequiredArgsConstructor
public class UploadPostFacade {
    private final S3ImageService s3ImageService;
    private final FileService fileService;
    private final UploadPostService uploadPostService;

    public void uploadPost(UploadRequest uploadRequest, MultipartFile file) {
        Long postId = null;
        
        try {
            FileDataDTO filedata = fileService.getFileData(file);
            String s3_url = s3ImageService.getS3url(filedata);

            postId = uploadPostService.uploadPost(uploadRequest, s3_url);

            // s3에서 예외발생시, post post_tag tag table에서 삭제
            s3ImageService.uploadImageWithId(file.getBytes(), filedata);
        } catch (Exception e) {
            log.error("Failed to upload image: error={}", e.getMessage(), e);

            if (postId != null) {
                log.info("Executing compensation transaction: Deleting post {}", postId);
                uploadPostService.deletePost(postId);
            }

            throw new RuntimeException("S3 upload failed: " + e.getMessage(), e);
        }

    }
}
