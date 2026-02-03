package com.example.Post.DTO;

import java.util.List;

public record UploadRequest(
    Long user_id,
    String title,
    String content,
    List<String> tags
) {}
