import re
from SysMLParser import SysMLParser
from Neo4jUtils import Neo4jUtils


def camel_to_snake(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).upper()


class Convertor:
    def __init__(self, sysml_path, neo4j_uri, neo4j_username, neo4j_password):
        self.sysml_parser = SysMLParser(sysml_path)
        self.neo4j_utils = Neo4jUtils(neo4j_uri, neo4j_username, neo4j_password)

    def close(self):
        self.neo4j_utils.close()

    def add_classes(self):
        count = 0
        class_map = self.sysml_parser.get_class()
        for class_name, class_attrib in class_map.items():
            self.neo4j_utils.add_node("class", class_name)
            self.neo4j_utils.set_node_properties("class", class_name, class_attrib)
            count += 1
        activity_lst = self.sysml_parser.get_activity()
        for activity_name in activity_lst:
            self.neo4j_utils.add_node("activity", activity_name)
            count += 1
        print("insert class nodes: ", count)

    def add_generalization(self):
        count = 0
        generalization_map = self.sysml_parser.get_generalization()
        for son, parent in generalization_map.items():
            self.neo4j_utils.add_relationship(son, parent, "SUB_CLASS_OF")
            count += 1
        print("insert generalization relationships: ", count)

    def add_association(self):
        count = 0
        association_lst = self.sysml_parser.get_association()
        for association in association_lst:
            source = association[0]
            rel_type = association[1]
            target = association[2]
            self.neo4j_utils.add_relationship(source, target, camel_to_snake(rel_type))
            count += 1
        print("insert association relationships: ", count)
