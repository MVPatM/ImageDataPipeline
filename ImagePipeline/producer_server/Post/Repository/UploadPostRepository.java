package com.example.Post.Repository;

import org.springframework.stereotype.Repository;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import com.example.Entity.Post;

@Repository
public interface UploadPostRepository extends JpaRepository<Post, Long> {
    // get post
    Optional<Post> findById(Long id);
}
