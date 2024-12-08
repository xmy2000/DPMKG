package com.xmy.controller;

import com.xmy.domain.Graph;
import com.xmy.service.GraphService;
import com.xmy.utils.Neo4jUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/graph")
public class GraphController {
    private String uri = "bolt://localhost:7687";
    private String user = "neo4j";
    private String password = "xmy200408";

    @Autowired
    private GraphService graphService;

    private Neo4jUtils neo4jUtils = new Neo4jUtils(uri, user, password);

    @GetMapping("/list")
    public Graph list() {
        return graphService.list(neo4jUtils);
    }

    //    http://localhost:3001/api/graph/GetNodeProperty?id=141
    @GetMapping("/GetNodeProperty")
    public String getNodeProperty(@RequestParam(value = "id") Integer nodeId) {
        System.out.println("click node: " + nodeId);
        return graphService.getNodeProperty(neo4jUtils, nodeId);
    }
}
