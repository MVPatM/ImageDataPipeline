package com.example.Post.Service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.example.Post.DTO.OnePostResponse;
import com.example.Post.DTO.ShowOnePostResponse;
import com.example.Post.DTO.S3urlResponse;
import com.example.Post.DTO.TagResponse;
import com.example.Post.Repository.ShowPostRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class ShowOnePostFacade {
    private final ShowPostService showPostService; // get post detail
    private final S3ImageService s3ImageService; // get image presigned url
    private final ShowPostRepository showPostRepository; // get tags

    // get post info > get tag name > get presigend url
    public ShowOnePostResponse showOnePost(Long post_id) {
        OnePostResponse onePostResponse = showPostService.getPost(post_id);

        List<String> tagNames = showPostRepository.findTagNamesByPostId(post_id);
        TagResponse tagResponse = new TagResponse(tagNames);

        String presignedUrl = s3ImageService.getPresignedUrl(onePostResponse.imageUrl());
        S3urlResponse s3urlResponse = new S3urlResponse(presignedUrl);

        return new ShowOnePostResponse(onePostResponse, s3urlResponse, tagResponse);
    }
}
