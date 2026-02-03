package com.example.Post.Service;

import com.example.Entity.Post;
import com.example.Post.DTO.ShowPostResponse;
import com.example.Post.DTO.OnePostResponse;
import com.example.Post.DTO.ShowPostListResponse;
import com.example.Post.Repository.ShowPostRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.data.domain.Slice;

import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class ShowPostService {
    private final ShowPostRepository showpostRepository;

    @Transactional(readOnly = true)
    public ShowPostListResponse getPosts(int page, int count) {
        // Validation (page 1 indexed)
        if (page < 1)
            page = 1;

        PageRequest pageRequest = PageRequest.of(page - 1, count);
        Slice<Post> postPage = showpostRepository.findAllByOrderByUpdatedAtDesc(pageRequest);
        long postCount = showpostRepository.count();

        List<ShowPostResponse> posts = postPage.stream()
                .map(post -> new ShowPostResponse(post.getId(), post.getTitle(), post.getUser_id().getId()))
                .collect(Collectors.toList());

        return new ShowPostListResponse(postCount, posts, "Success");
    }

    @Transactional(readOnly = true)
    public OnePostResponse getPost(Long post_id) {
        return showpostRepository.findPostDetailById(post_id)
                .orElseThrow(() -> new RuntimeException("Post not found with id: " + post_id));
    }
}
