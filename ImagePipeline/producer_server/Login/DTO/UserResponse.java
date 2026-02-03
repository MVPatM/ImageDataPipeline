package com.example.Login.DTO;

import java.time.LocalDateTime;

public record UserResponse(
    Long id,
    String username,
    LocalDateTime createdAt
) {}
