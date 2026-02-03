package com.example.Entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "post_tag", uniqueConstraints = {
    @UniqueConstraint(columnNames = {"post_id", "tag_id"})
})
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PostTag {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "post_id", nullable = false)
    private Post post_id;
    
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "tag_id", nullable = false)
    private Tag tag_id;
    
    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;
}


/*
CREATE TABLE post_tag (
    id BIGINT NOT NULL AUTO_INCREMENT,
    post_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_post_tag (post_id, tag_id),

    CONSTRAINT fk_post_tag_posts
        FOREIGN KEY (post_id)
        REFERENCES posts (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_post_tag_tags
        FOREIGN KEY (tag_id)
        REFERENCES tags (id)
        ON DELETE CASCADE
);
*/