package com.example.FileUpload.Repository;

import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Slice;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import com.example.FileUpload.Entity.DeadLetter;

@Repository
public interface DeadLetterRepository extends JpaRepository<DeadLetter, Long> {
    // 페이징을 이용한 배치 조회 (OOM 방지)
    Slice<DeadLetter> findBy(Pageable pageable);
    
    // key 값으로 삭제
    @Modifying
    @Query("DELETE FROM DeadLetter d WHERE d.key = :key")
    int deleteByKey(@Param("key") byte[] key);
}
