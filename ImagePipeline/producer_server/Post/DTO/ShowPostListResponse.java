package com.example.Post.DTO;

import java.util.List;

public record ShowPostListResponse(
        Long postCount,
        List<ShowPostResponse> posts,
        String message) {
}