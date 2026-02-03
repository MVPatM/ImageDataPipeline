package com.example.Entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "posts")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Post {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private User user_id;

    // s3 url
    @Column(name = "image_url", nullable = false, length = 1000)
    private String imageUrl;

    // 제목
    @Column(name = "title", nullable = false, length = 500)
    private String title;

    // 내용
    @Column(name = "content", length = 2000)
    private String content;

    // Pending, Active
    @Column(name = "status", nullable = false, length = 100)
    private String status;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @OneToMany(mappedBy = "post_id", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<PostTag> postTags = new ArrayList<>();
}

/* 
CREATE TABLE posts (
    id BIGINT NOT NULL AUTO_INCREMENT,

    user_id BIGINT NOT NULL,

    image_url VARCHAR(1000) NOT NULL,
    title VARCHAR(2000) NOT NULL,
    content VARCHAR(2000),
    status VARCHAR(100) NOT NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    KEY idx_posts_user_id (user_id),
    KEY idx_posts_updated_at_desc (updated_at DESC),

    CONSTRAINT fk_posts_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
)
*/