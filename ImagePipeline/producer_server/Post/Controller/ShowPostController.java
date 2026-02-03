package com.example.Post.Controller;

import java.util.List;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.PathVariable;

import com.example.Post.DTO.ShowPostListResponse;
import com.example.Post.DTO.ShowOnePostResponse;
import com.example.Post.Service.ShowOnePostFacade;
import com.example.Post.Service.ShowPostService;

@Slf4j
@RestController
@RequiredArgsConstructor
public class ShowPostController {
    private final ShowPostService showPostService;
    private final ShowOnePostFacade showOnePostFacade;

    @GetMapping("/post")
    public ResponseEntity<ShowPostListResponse> getPosts(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        try {
            ShowPostListResponse listShowPostResponse = showPostService.getPosts(page, size);

            return ResponseEntity.ok(listShowPostResponse);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(new ShowPostListResponse(0L, List.of(), e.getMessage()));
        }
    }

    @GetMapping("/post/{post_id}")
    public ResponseEntity<ShowOnePostResponse> getPost(@PathVariable Long post_id) {
        try {
            ShowOnePostResponse showOnePostResponse = showOnePostFacade.showOnePost(post_id);
            return ResponseEntity.ok(showOnePostResponse);
        } catch (Exception e) {
            log.error("Error while getting post: error={}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
        }
    }
}
