package com.xmy.service;

import com.xmy.domain.Graph;
import com.xmy.utils.Neo4jUtils;

public interface GraphService {
    Graph list(Neo4jUtils neo4jUtils);

    String getNodeProperty(Neo4jUtils neo4jUtils, Integer nodeId);
}
