from neo4j import GraphDatabase


class Neo4jUtils:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.driver.verify_connectivity()
        print("Neo4j connect successfully!")

    def addNode(self, id, name, label):
        cypher = "MERGE (n:" + label + " {ID: $id, name: $name})"
        self.driver.execute_query(
            cypher,
            id=id, name=name,
            database_="neo4j"
        )

    def addRelationByName(self, source, target, rel_name):
        cypher = "MATCH (source {name:$n1}), (target {name:$n2}) MERGE (source)-[r:" + rel_name + "]->(target)"
        self.driver.execute_query(
            cypher,
            n1=source, n2=target,
            database_="neo4j"
        )

    def addRelationById(self, source_label, source_id, target_type, target_id, rel_name):
        cypher = "MATCH (source:" + source_label + " {ID:$n1}), (target:" + target_type + " {ID:$n2}) MERGE (source)-[r:" + rel_name + "]->(target)"
        self.driver.execute_query(
            cypher,
            n1=source_id, n2=target_id,
            database_="neo4j"
        )

    def addRelationByIdAndName(self, source_label, source_id, target_type, target_name, rel_name):
        cypher = "MATCH (source:" + source_label + " {ID:$n1}), (target:" + target_type + " {name:$n2}) MERGE (source)-[r:" + rel_name + "]->(target)"
        self.driver.execute_query(
            cypher,
            n1=source_id, n2=target_name,
            database_="neo4j"
        )

    def addNodeProperty(self, node, prop, value):
        if type(value) == str:
            cypher = "MERGE (node {name:$n1}) ON MATCH SET node." + prop + "=\"" + str(value) + "\""
        else:
            cypher = "MERGE (node {name:$n1}) ON MATCH SET node." + prop + "=" + str(value)
        self.driver.execute_query(
            cypher,
            n1=node,
            database_="neo4j"
        )

    def addNodePropertyById(self, node_type, node_id, prop, value):
        if type(value) == str:
            cypher = "MERGE (node:" + node_type + " {ID:'" + node_id + "'}) ON MATCH SET node." + prop + "=\"" + str(
                value) + "\""
        else:
            cypher = "MERGE (node:" + node_type + " {ID:'" + node_id + "'}) ON MATCH SET node." + prop + "=" + str(
                value)
        self.driver.execute_query(
            cypher,
            database_="neo4j"
        )

    def deleteAll(self):
        cypher = "MATCH (n) DETACH DELETE n"
        self.driver.execute_query(
            cypher,
            database_="neo4j"
        )

    def findID(self, feature_id):
        cypher = ("MATCH (p:Part)-[:HAS_FEATURES]->(f:Feature {ID:'" + feature_id + "'}), "
                                                                                    "(p)-[:HAS_PROCESS]->(r:`工艺路线`)-[:HAS_COMPONENT]->(gx:`工序`)-[:HAS_COMPONENT]->(gb:`工步`) "
                                                                                    "return gx.ID")
        records, summary, keys = self.driver.execute_query(
            cypher,
            database_="neo4j"
        )
        return records[0][0]
