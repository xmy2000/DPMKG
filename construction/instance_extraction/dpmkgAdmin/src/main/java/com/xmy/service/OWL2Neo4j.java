package com.xmy.service;

import com.xmy.common.MyException;
import com.xmy.utils.Neo4jUtils;
import com.xmy.utils.OWLReadUtils;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.FileNotFoundException;
import java.util.List;
import java.util.Map;
import java.util.Set;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class OWL2Neo4j {
    private String neo4jUri;
    private String neo4jUsername;
    private String neo4jPassword;
    private String OWLFileName;
    private Neo4jUtils neo4jUtils;
    private OWLReadUtils owlReadUtils;

    private int nodeCount = 0;
    private int SCORelationCount = 0;
    private int classRelationCount = 0;
    private int classPropertyCount = 0;

    public OWL2Neo4j(String neo4jUri, String neo4jUsername, String neo4jPassword, String OWLFileName) throws FileNotFoundException {
        this.neo4jUri = neo4jUri;
        this.neo4jUsername = neo4jUsername;
        this.neo4jPassword = neo4jPassword;
        this.OWLFileName = OWLFileName;
        this.neo4jUtils = new Neo4jUtils(neo4jUri, neo4jUsername, neo4jPassword);
        this.owlReadUtils = new OWLReadUtils(OWLFileName);
    }

    public void convert() throws MyException {
        neo4jUtils.deleteAll();

        System.out.println("==========Step1: 节点创建...==========");
        convertClassToNode();

        System.out.println("==========Step2: SCO关系创建...==========");
        addSCORelation();

        System.out.println("==========Step3: 节点关系创建...==========");
        addClassRelation();

        System.out.println("==========Step4: 节点属性创建...==========");
        addClassProperty();

        System.out.println("==========基于OWL文件的图数据库初始化完成==========");
        System.out.println("创建节点数: " + nodeCount);
        System.out.println("创建SCO关系数: " + SCORelationCount);
        System.out.println("创建节点关系数: " + classRelationCount);
        System.out.println("创建节点属性数: " + classPropertyCount);
    }

    public void convertClassToNode() throws MyException {
        Map<String, String> classMap = owlReadUtils.traverseClassNameMap();
        for (String name : classMap.keySet()) {
            String type = classMap.get(name);
            switch (type) {
                case "package" -> neo4jUtils.addNode("术语", name);
                case "class" -> neo4jUtils.addNode("实体类", name);
                case "activity" -> neo4jUtils.addNode("活动类", name);
                default -> throw new MyException("节点添加出错: " + name + "->" + type);
            }
            nodeCount++;
        }
    }

    public void addSCORelation() {
        Map<String, String> classMap = owlReadUtils.traverseClassNameMap();
        for (String name : classMap.keySet()) {
            Set<String> superClass = owlReadUtils.findSuperClass(name);
            if (superClass.size() == 0) {
                continue;
            }
            for (String aClass : superClass) {
                neo4jUtils.addSCORelationship(aClass, name);
                SCORelationCount++;
            }
        }
    }

    public void addClassRelation() {
        Map<String, String> classMap = owlReadUtils.traverseClassNameMap();
        for (String name : classMap.keySet()) {
            String type = classMap.get(name);
            if (type.equals("package")) {
                continue;
            }
            Map<String, List<String>> map = owlReadUtils.findObjectProperty(name);
            List<String> r_list = map.get("relation");
            List<String> c_list = map.get("class");
            if (r_list.size() == 0) {
                continue;
            }
            for (int i = 0; i < r_list.size(); i++) {
                String r = r_list.get(i);
                String c = c_list.get(i);
                neo4jUtils.addClassRelationship(name, r, c);
                classRelationCount++;
            }
        }
    }

    public void addClassProperty() {
        Map<String, String> classMap = owlReadUtils.traverseClassNameMap();
        for (String name : classMap.keySet()) {
            String type = classMap.get(name);
            if (type.equals("package") || type.equals("activity")) {
                continue;
            }
            Map<String, List<String>> map = owlReadUtils.findDataProperty(name);
            List<String> p_list = map.get("property");
            List<String> t_list = map.get("type");
            if (p_list.size() == 0) {
                continue;
            }
            for (int i = 0; i < p_list.size(); i++) {
                String p = p_list.get(i);
                String t = t_list.get(i);
                neo4jUtils.addClassProperty(name, p, t);
                classPropertyCount++;
            }
        }
    }

    public static void main(String[] args) throws FileNotFoundException, MyException {
        String uri = "bolt://localhost:7687";
        String user = "neo4j";
        String password = "xxxxxx";
        String owl = "xxx.owl";
        OWL2Neo4j u2n = new OWL2Neo4j(uri, user, password, owl);
        u2n.convert();
    }
}
