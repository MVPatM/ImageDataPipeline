package com.example.FileUpload.Entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.persistence.*;

@Entity
@Table(name = "DeadLetter")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DeadLetter {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "`key`", nullable = false, columnDefinition = "VARBINARY(100)")
    private byte[] key;
    
    @Lob
    @Column(name = "`value`", nullable = false, columnDefinition = "MEDIUMBLOB")
    private byte[] value;
    
    @Column(name = "topic", nullable = false, length = 255)
    private String topic;
}
