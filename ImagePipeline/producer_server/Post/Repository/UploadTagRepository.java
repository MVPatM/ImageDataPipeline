package com.example.Post.Repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.example.Entity.Tag;
import java.util.List;
import java.util.Optional;

@Repository
public interface UploadTagRepository extends JpaRepository<Tag, Long> {
    Optional<Tag> findByName(String name);
    
    List<Tag> findByNameIn(List<String> names);

    @Query("SELECT t.name FROM Tag t WHERE t.name IN :names")
    List<String> findNamesByNames(@Param("names") List<String> names);

    @Query("SELECT t.id FROM Tag t WHERE t.name IN :names")
    List<Long> findIdsByNames(@Param("names") List<String> names);
}
