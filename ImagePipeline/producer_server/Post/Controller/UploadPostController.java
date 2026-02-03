package com.example.Post.Controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.example.Post.Service.UploadPostService;
import com.example.Post.Service.UploadPostFacade;
import com.example.Post.DTO.UploadRequest;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;
import java.util.HashMap;

@Slf4j
@RestController
@RequiredArgsConstructor
public class UploadPostController {
    private final UploadPostService uploadPostService;
    private final UploadPostFacade uploadPostFacade;

    @PostMapping(value = "/post/upload", consumes = "multipart/form-data")
    public ResponseEntity<Map<String, Object>> uploadPost(
            @RequestPart("request") UploadRequest uploadRequest,
            @RequestPart("file") MultipartFile file) {
        try {

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            // s3에서 문제가 발생하면 보상 트랜잭션 수행하기

            uploadPostFacade.uploadPost(uploadRequest, file);

            return ResponseEntity.ok().body(response);
        } catch (Exception e) {
            log.error("Failed to upload image: error={}", e.getMessage(), e);
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", e.getMessage());
            return ResponseEntity.status(500).body(response);
        }
    }

    @GetMapping("/post/{id}/delete")
    public ResponseEntity<String> deletePost(@PathVariable Long id) {
        try {
            uploadPostService.deletePost(id);
            return ResponseEntity.ok("Post deleted successfully");
        } catch (Exception e) {
            log.error("Error while deleting post: error={}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error while deleting post");
        }
    }
}