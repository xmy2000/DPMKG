package com.xmy.service.impl;

import com.alibaba.fastjson.JSONObject;
import com.xmy.config.GraphConfig;
import com.xmy.domain.Graph;
import com.xmy.domain.Line;
import com.xmy.domain.Node;
import com.xmy.service.GraphService;
import com.xmy.utils.Neo4jUtils;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
public class GraphServiceImpl implements GraphService {
    @Override
    public Graph list(Neo4jUtils neo4jUtils) {
        List<Node> nodeList = new ArrayList<>();
        List<Line> lineList = new ArrayList<>();

        List<Map> nodes = neo4jUtils.listNode();
        for (Map node : nodes) {
            String id = node.get("id").toString();
            String text = node.get("name").toString();
            String label = node.get("label").toString().replace("[", "").replace("]", "");
            String color = GraphConfig.nodeColor.get(label);
            Integer shape = GraphConfig.nodeShape.get(label);
            nodeList.add(new Node(id, text, color, color, shape));
        }

        List<Map> lines = neo4jUtils.listLine();
        for (Map line : lines) {
            String id = line.get("id").toString();
            String type = line.get("type").toString();
            String source = line.get("source").toString();
            String target = line.get("target").toString();
            lineList.add(new Line(source, target, type));
        }

        return new Graph("0", nodeList, lineList);
    }

    @Override
    public String getNodeProperty(Neo4jUtils neo4jUtils, Integer nodeId) {
        JSONObject jsonObject = new JSONObject();

        String nodeProperty = neo4jUtils.getNodeProperty(nodeId);
        nodeProperty = nodeProperty.replace("{", "").replace("}", "");
        String[] split = nodeProperty.split(", ");
        for (String s : split) {
            String name = s.split("=")[0];
            String value = s.split("=")[1];
            jsonObject.put(name, value);
        }
        return JSONObject.toJSONString(jsonObject);
    }
}
