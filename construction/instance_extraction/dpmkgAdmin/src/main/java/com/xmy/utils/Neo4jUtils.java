package com.xmy.utils;

import org.neo4j.driver.*;
import org.neo4j.driver.Record;

import java.util.*;
import java.util.logging.Level;

import static org.neo4j.driver.Values.parameters;

public class Neo4jUtils implements AutoCloseable {
    private final Driver driver;

    public Neo4jUtils(String uri, String user, String password) {
        Config config = Config.builder().withLogging(Logging.console(Level.INFO)).build();
        driver = GraphDatabase.driver(uri, AuthTokens.basic(user, password), config);
    }

    @Override
    public void close() throws Exception {
        driver.close();
    }

    public void addNode(String label, String name) {
        String query = "MERGE (n:" + label + " {name: $value})";
        try (Session session = driver.session()) {
            session.executeWriteWithoutResult(tx ->
                    tx.run(query, parameters("value", name))
                            .consume()
            );
        }
    }

    public void deleteAll() {
        try (Session session = driver.session()) {
            session.executeWriteWithoutResult(tx ->
                    tx.run("MATCH (n) DETACH DELETE n")
                            .consume()
            );
        }
    }

    public void addSCORelationship(String superClass, String subClass) {
        String query = "MATCH (father {name:$n1}), (son {name:$n2}) MERGE (son)-[r:SUB_CLASS_OF]->(father)";
        try (Session session = driver.session()) {
            session.executeWriteWithoutResult(tx ->
                    tx.run(query, parameters("n1", superClass, "n2", subClass))
                            .consume()
            );
        }
    }

    public void addClassRelationship(String source, String type, String target) {
        String r_name = CommonUtils.humpToUnderline(type).toUpperCase();
        String query = "MATCH (source {name:$n1}), (target {name:$n2}) MERGE (source)-[r:" + r_name + "]->(target)";
        try (Session session = driver.session()) {
            session.executeWriteWithoutResult(tx ->
                    tx.run(query, parameters("n1", source, "n2", target))
                            .consume()
            );
        }
    }

    public void addNodeRelationship(String source, String type, String target) {
        String query = "MATCH (source {name:$n1}), (target {name:$n2}) MERGE (source)-[r:" + type + "]->(target)";
        try (Session session = driver.session()) {
            session.executeWriteWithoutResult(tx ->
                    tx.run(query, parameters("n1", source, "n2", target))
                            .consume()
            );
        }
    }

    public void addClassProperty(String node, String property, String content) {
        StringBuffer sb = new StringBuffer(property);
        int flag = -1;
        do {
            flag = sb.indexOf("/");
            if (flag != -1) {
                sb.deleteCharAt(flag);
            }
        } while (flag != -1);

        String query = "MERGE (node {name:$n1}) ON MATCH SET node." + sb.toString() + "=\"" + content + "\"";
        try (Session session = driver.session()) {
            session.executeWriteWithoutResult(tx ->
                    tx.run(query, parameters("n1", node))
                            .consume()
            );
        }
    }

    public List<Map> findNodeOutRel(String nodeName) {
        List<Map> out_rel_list = new ArrayList<>();
        String query = "match (n:`实体`)-[:SUB_CLASS_OF*1..5]->(m:`实体类`)<-[:HAS_PART*0..3]-(a:`实体类`)-[:SUB_CLASS_OF]->(:`术语`)," +
                "(a)-[r:!SUB_CLASS_OF]->(t:`实体类`)" +
                "where n.name=\"" + nodeName + "\"" +
                "return type(r) as rel_type, t.name as node_name";

        try (Session session = driver.session()) {
            session.executeRead(tx -> {
                Result result = tx.run(query);
                while (result.hasNext()) {
                    Record next = result.next();
                    out_rel_list.add(next.asMap());
                }
                return out_rel_list;
            });
        }

        // [{rel_type=IDENTIFY_BY, node_name=刀具序列号标识符}, {rel_type=WORK_ON, node_name=零件}]
        return out_rel_list;
    }

    public List<Map> findNodeInRel(String nodeName) {
        List<Map> in_rel_list = new ArrayList<>();
        String query = "match (n:`实体`)-[:SUB_CLASS_OF*1..5]->(m:`实体类`)<-[:HAS_PART*0..3]-(a:`实体类`)-[:SUB_CLASS_OF]->(:`术语`)," +
                "(a)<-[r:!SUB_CLASS_OF]-(t:`实体类`)" +
                "where n.name=\"" + nodeName + "\"" +
                "return type(r) as rel_type, t.name as node_name";

        try (Session session = driver.session()) {
            session.executeRead(tx -> {
                Result result = tx.run(query);
                while (result.hasNext()) {
                    Record next = result.next();
                    in_rel_list.add(next.asMap());
                }
                return in_rel_list;
            });
        }

        // [{rel_type=IDENTIFY_BY, node_name=刀具序列号标识符}, {rel_type=WORK_ON, node_name=零件}]
        return in_rel_list;
    }

    public Set<Map> findEntity(String nodeName) {
        Set<Map> entity_set = new HashSet<>();
        String query = "match (n:`实体`)-[:SUB_CLASS_OF]->(t:`实体类`)-[:(SUB_CLASS_OF|HAS_PART)*1..5]-(m:`实体类`) " +
                "where m.name=\"" + nodeName + "\" " +
                "return n.name as name, n.uid as uid";
        try (Session session = driver.session()) {
            session.executeRead(tx -> {
                Result result = tx.run(query);
                while (result.hasNext()) {
                    Record next = result.next();
                    entity_set.add(next.asMap());
                }
                return entity_set;
            });
        }
        return entity_set;
    }

    public List<Map> listNode() {
        List<Map> nodes = new ArrayList<>();
        String query = "match (n) return id(n) as id, n.name as name, labels(n) as label";
        try (Session session = driver.session()) {
            session.executeRead(tx -> {
                Result result = tx.run(query);
                while (result.hasNext()) {
                    Record next = result.next();
                    nodes.add(next.asMap());
                }
                return nodes;
            });
        }
        return nodes;
    }

    public List<Map> listLine() {
        List<Map> lines = new ArrayList<>();
        String query = "MATCH (n)-[r]->(m) RETURN id(r) as id, type(r) as type, id(n) as source, id(m) as target";
        try (Session session = driver.session()) {
            session.executeRead(tx -> {
                Result result = tx.run(query);
                while (result.hasNext()) {
                    Record next = result.next();
                    lines.add(next.asMap());
                }
                return lines;
            });
        }
        return lines;
    }

    public String getNodeProperty(Integer nodeId) {
        final String[] property = new String[1];
        String query = "match (n) where id(n)=" + nodeId + " return properties(n) as property";
        try (Session session = driver.session()) {
            session.executeRead(tx -> {
                Result result = tx.run(query);
                property[0] = result.next().asMap().get("property").toString();
                return property[0];
            });
        }
        return property[0];
    }

    public static void main(String[] args) {
        String uri = "bolt://localhost:7687";
        String user = "neo4j";
        String password = "xmy200408";
        Neo4jUtils utils = new Neo4jUtils(uri, user, password);
//        List<Map> nodeRel = utils.findNodeRel("车槽刀_11904300053");
//        System.out.println(nodeRel);
//        Set<Map> entity = utils.findEntity("刀具");
//        System.out.println(entity);
        System.out.println(utils.getNodeProperty(0));
    }
}
