package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import org.springframework.core.Ordered;
import org.springframework.retry.annotation.EnableRetry;

@EnableRetry(order = Ordered.HIGHEST_PRECEDENCE)
@SpringBootApplication
public class ApiServerApplication {

	public static void main(String[] args) {
		SpringApplication.run(ApiServerApplication.class, args);
	}
}
