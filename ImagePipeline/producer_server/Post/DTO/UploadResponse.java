package com.example.Post.DTO;

import java.time.LocalDateTime;
import java.util.List;

public record UploadResponse(
    Long id,
    String title,
    String content,
    List<TagResponse> tags,
    LocalDateTime updatedAt
) {}
