package com.example.Login.DTO;

public record AuthResponse(
    Long user_id,
    String username,
    String message
) {}
