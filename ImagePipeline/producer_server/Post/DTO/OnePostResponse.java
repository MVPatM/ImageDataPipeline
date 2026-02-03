package com.example.Post.DTO;

import java.time.LocalDateTime;

public record OnePostResponse(
    String title,
    String content,
    String imageUrl,
    Long user_id,
    LocalDateTime updatedAt
) {}
