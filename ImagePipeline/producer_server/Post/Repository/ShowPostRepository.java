package com.example.Post.Repository;

import org.springframework.data.domain.Slice;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import com.example.Entity.Post;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

import com.example.Post.DTO.OnePostResponse;

@Repository
public interface ShowPostRepository extends JpaRepository<Post, Long> {

    // post id로 imageUrl 조회
    @Query("SELECT p.imageUrl FROM Post p WHERE p.id = :postId")
    Optional<String> findImageUrlById(@Param("postId") Long postId);

    // post id로 title, content, imageUrl, user_id, updatedAt 조회
    @Query("SELECT p.title AS title, p.content AS content, p.imageUrl AS imageUrl, p.user_id.id AS user_id, p.updatedAt AS updatedAt FROM Post p WHERE p.id = :postId")
    Optional<OnePostResponse> findPostDetailById(@Param("postId") Long postId);

    // 10개 post보여주는 logic
    // id(primary key), title
    // order by updatedAt desc
    Slice<Post> findAllByOrderByUpdatedAtDesc(Pageable pageable);

    // post id로 해당 post에 속한 tag들의 이름을 조회 (PostTag와 Tag 테이블 조인)
    @Query("SELECT t.name FROM PostTag pt JOIN pt.tag_id t WHERE pt.post_id.id = :postId")
    List<String> findTagNamesByPostId(@Param("postId") Long postId);
}
