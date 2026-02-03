package com.example.Login.Service;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import com.example.Login.Repository.UserRepository;

import lombok.RequiredArgsConstructor;

import com.example.Entity.User;
import com.example.Login.DTO.LoginRequest;
import com.example.Login.DTO.AuthResponse;
import com.example.Login.DTO.SignupRequest;

import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class LoginService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Transactional
    public AuthResponse signup(SignupRequest request) {
        if (userRepository.existsByUsername(request.username())) {
            throw new RuntimeException("Username already exists");
        }

        User user = User.builder()
                .username(request.username())
                .password(passwordEncoder.encode(request.password()))
                .build();

        User savedUser = userRepository.save(user);

        return new AuthResponse(
            savedUser.getId(),
            savedUser.getUsername(),
            "Signup successful"
        );
    }

    @Transactional(readOnly = true)
    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.username())
                .orElseThrow(() -> new RuntimeException("Invalid username or password"));

        if (!passwordEncoder.matches(request.password(), user.getPassword())) {
            throw new RuntimeException("Invalid username or password");
        }

        return new AuthResponse(
                user.getId(),
                user.getUsername(),
                "Login successful"
        );
    }
}
