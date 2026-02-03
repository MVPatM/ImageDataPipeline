package com.example.Post.DTO;

public record ShowOnePostResponse(
    OnePostResponse onePostResponse,
    S3urlResponse s3urlResponse,
    TagResponse tagResponse
) {}
