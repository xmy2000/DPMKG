from neo4j import GraphDatabase


class Neo4jUtils:
    def __init__(self, uri, user, password, database="neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        self.driver.verify_connectivity()

    def close(self):
        self.driver.close()

    def add_node(self, label, name):
        cypher = f"MERGE (:{label} {{name: $name}})"
        self.driver.execute_query(cypher, name=name, database_=self.database)

    def set_node_properties(self, label, name, properties):
        cypher = f"MATCH (n:{label} {{name: $name}}) SET n += $properties"
        self.driver.execute_query(cypher, name=name, properties=properties, database_=self.database)

    def add_relationship(self, source, target, rel_type):
        cypher = f"""
        MATCH
            (source {{name: $source}}),
            (target {{name: $target}})
        MERGE (source)-[r:{rel_type}]->(target)
        """
        self.driver.execute_query(cypher, source=source, target=target, database_=self.database)

    def delete_all(self):
        self.driver.execute_query("MATCH (n) DETACH DELETE n", database_=self.database)

    def delete_node_with_label(self, label):
        self.driver.execute_query(f"MATCH (n:{label}) DETACH DELETE n", database_=self.database)
