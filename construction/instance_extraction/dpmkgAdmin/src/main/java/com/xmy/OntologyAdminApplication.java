package com.xmy;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.xmy.mapper")
public class OntologyAdminApplication {

    public static void main(String[] args) {
        SpringApplication.run(OntologyAdminApplication.class, args);
    }

}
