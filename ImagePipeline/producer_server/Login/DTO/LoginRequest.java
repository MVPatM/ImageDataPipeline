package com.example.Login.DTO;

public record LoginRequest(
        String username,
        String password
    ) {}