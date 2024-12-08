package com.xmy.domain;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Node {
    private String id;
    private String text;
    private String color;
    private String borderColor;
    private Integer nodeShape = 0;
}
