package com.example.Login.Controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import com.example.Login.Service.LoginService;

import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.HttpStatus;

import com.example.Login.DTO.LoginRequest;
import com.example.Login.DTO.SignupRequest;
import com.example.Login.DTO.AuthResponse;

@RestController
@RequiredArgsConstructor
public class LoginController {
    private final LoginService loginService;
    
    @PostMapping("/login/signup")
    public ResponseEntity<AuthResponse> signup(@RequestBody SignupRequest request) {
        try {
            AuthResponse response = loginService.signup(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        }
        catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body(new AuthResponse(null, null, e.getMessage()));
        }
        catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(new AuthResponse(null, null, "Server occurs error"));
        }
    }
    
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@RequestBody LoginRequest request) {
        try {
            AuthResponse response = loginService.login(request);
        return ResponseEntity.ok(response);
        }
        catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(new AuthResponse(null, null, e.getMessage()));
        }
        catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(new AuthResponse(null, null, "Server occurs error"));
        }
    }
}
