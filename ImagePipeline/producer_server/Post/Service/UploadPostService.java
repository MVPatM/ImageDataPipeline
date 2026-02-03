package com.example.Post.Service;

import com.example.Login.Repository.UserRepository;
import com.example.Post.DTO.UploadRequest;
import com.example.Entity.Post;
import com.example.Entity.PostTag;
import com.example.Entity.Tag;
import com.example.Post.Repository.UploadPostRepository;
import com.example.Post.Repository.UploadTagRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Retryable;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.jdbc.core.BatchPreparedStatementSetter;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Service
@RequiredArgsConstructor
public class UploadPostService {
    private final UploadPostRepository uploadPostRepository;
    private final UploadTagRepository uploadTagRepository;
    private final UserRepository userRepository;
    private final JdbcTemplate jdbcTemplate;

    @Transactional
    @Retryable(retryFor = { Exception.class }, maxAttempts = 3, backoff = @Backoff(delay = 1000))
    public Long uploadPost(UploadRequest uploadRequest, String s3_url) {
        // create post
        Post post = Post.builder()
                .user_id(userRepository.getReferenceById(uploadRequest.user_id()))
                .title(uploadRequest.title())
                .content(uploadRequest.content())
                .status("PENDING")
                .imageUrl(s3_url)
                .build();

        // create tag using jdbctemplate and get tagid
        // find existing tag names
        Set<String> set = new HashSet<>(uploadTagRepository.findNamesByNames(uploadRequest.tags()));

        // get not existing tag names
        List<String> notexistNames = new ArrayList<>();
        for (String tagName : uploadRequest.tags()) {
            if (!set.contains(tagName)) {
                notexistNames.add(tagName);
            }
        }

        // bulk insert not existing tag names and get all tagids
        BulkInsertTags(notexistNames);
        List<Long> tagids = uploadTagRepository.findIdsByNames(uploadRequest.tags());

        // create posttag
        for (Long tagid : tagids) {
            PostTag postTag = PostTag.builder()
                    .post_id(post)
                    .tag_id(uploadTagRepository.getReferenceById(tagid))
                    .build();

            post.getPostTags().add(postTag);
        }
        // uploadPostRepository.save(post);
        Long postId = InsertPost(post);
        BulkInsertPostTags(postId, tagids);

        return postId;
    }

    public void BulkInsertTags(List<String> tagNames) {
        String sql = "Insert into tags (name) values (?)";

        jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                ps.setString(1, tagNames.get(i));
            }

            @Override
            public int getBatchSize() {
                return tagNames.size();
            }
        });
    }

    public Long InsertPost(Post post) {
        String sql = "Insert into posts (user_id, title, content, image_url, status) values (?, ?, ?, ?, ?)";

        org.springframework.jdbc.support.KeyHolder keyHolder = new org.springframework.jdbc.support.GeneratedKeyHolder();

        jdbcTemplate.update(connection -> {
            PreparedStatement ps = connection.prepareStatement(sql, java.sql.Statement.RETURN_GENERATED_KEYS);
            ps.setLong(1, post.getUser_id().getId());
            ps.setString(2, post.getTitle());
            ps.setString(3, post.getContent());
            ps.setString(4, post.getImageUrl());
            ps.setString(5, post.getStatus());
            return ps;
        }, keyHolder);

        return keyHolder.getKey().longValue();
    }

    public void BulkInsertPostTags(Long postId, List<Long> tagIds) {
        String sql = "Insert into post_tag (post_id, tag_id) values (?, ?)";

        jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                ps.setLong(1, postId);
                ps.setLong(2, tagIds.get(i));
            }

            @Override
            public int getBatchSize() {
                return tagIds.size();
            }
        });
    }

    @Transactional
    public void uploadPostv2(UploadRequest uploadRequest, String s3_url) {
        org.springframework.util.StopWatch stopWatch = new org.springframework.util.StopWatch("UploadPostService");

        stopWatch.start("Create Post Object");
        // 1. Post 생성
        Post post = Post.builder()
                .user_id(userRepository.getReferenceById(uploadRequest.user_id()))
                .title(uploadRequest.title())
                .content(uploadRequest.content())
                .imageUrl(s3_url)
                .status("Active")
                .build();
        stopWatch.stop();

        stopWatch.start("Process Tags");
        // 2. Tag 처리 (있으면 가져오고, 없으면 생성)
        List<String> tagNames = uploadRequest.tags();
        if (tagNames != null && !tagNames.isEmpty()) {
            for (String tagName : tagNames) {
                // Tag가 이미 있으면 가져오고, 없으면 새로 생성
                Tag tag = uploadTagRepository.findByName(tagName)
                        .orElseGet(() -> uploadTagRepository.save(
                                Tag.builder().name(tagName).build()));
                // 3. PostTag 연결 (Post-Tag 관계)
                PostTag postTag = PostTag.builder()
                        .post_id(post)
                        .tag_id(tag)
                        .build();
                post.getPostTags().add(postTag);
            }
        }
        stopWatch.stop();

        stopWatch.start("Save Post");
        // 4. Post 저장 (CascadeType.ALL로 PostTag도 함께 저장됨)
        uploadPostRepository.save(post);
        stopWatch.stop();

        System.out.println(stopWatch.prettyPrint());
    }

    @Transactional
    public void deletePost(Long post_id) {
        uploadPostRepository.deleteById(post_id);
    }

    @Transactional
    public void uploadPostv3(UploadRequest uploadRequest, String s3_url) {
        // 1. Post 생성
        Post post = Post.builder()
                .user_id(userRepository.getReferenceById(uploadRequest.user_id()))
                .title(uploadRequest.title())
                .content(uploadRequest.content())
                .imageUrl(s3_url)
                .status("PENDING")
                .build();

        // 2. Tag 리스트 한번에 처리 (INSERT IGNORE)
        List<String> tagNames = uploadRequest.tags();
        BulkInsertTagsv1(tagNames);

        // 모든 태그 가져오기
        List<Long> tagIds = uploadTagRepository.findIdsByNames(tagNames);

        // 3. PostTag 연결
        for (Long tagId : tagIds) {
            PostTag postTag = PostTag.builder()
                    .post_id(post)
                    .tag_id(uploadTagRepository.getReferenceById(tagId))
                    .build();
            post.getPostTags().add(postTag);
        }

        uploadPostRepository.save(post);
    }

    public void BulkInsertTagsv1(List<String> tagNames) {
        String sql = "Insert ignore into tags (name) values (?)";

        jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                ps.setString(1, tagNames.get(i));
            }

            @Override
            public int getBatchSize() {
                return tagNames.size();
            }
        });
    }
}
