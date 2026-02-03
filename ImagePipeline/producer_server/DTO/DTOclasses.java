package com.example.DTO;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
class UserResponse {
    private Long id;
    private String username;
    private String email;
    private String profileImageUrl;
    private String bio;
    private LocalDateTime createdAt;
}

// Post DTOs
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
class PostCreateRequest {
    private String caption;
    private String content;
    private List<String> tags;
}

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
class PostResponse {
    private Long id;
    private UserResponse user;
    private List<TagResponse> tags;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

// Tag DTOs
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
class TagResponse {
    private Long id;
    private String name;
    private Integer usageCount;
    private LocalDateTime createdAt;
}