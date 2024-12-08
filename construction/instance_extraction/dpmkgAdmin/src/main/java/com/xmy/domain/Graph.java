package com.xmy.domain;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Graph {
    private String rootId;
    private List<Node> nodes;
    private List<Line> lines;
}
