import xml.etree.ElementTree as ET

NS = {
    'uml': "http://schema.omg.org/spec/UML/2.1",
    'xmi': "http://schema.omg.org/spec/XMI/2.1",
    'SysML': "http://www.omg.org/spec/SysML/20161101/SysML",
    'StandardProfileL2': "http://www.omg.org/spec/UML/20110701/StandardProfileL2.xmi"
}
SKIP_PACKAGE_NAMES = ['Map', 'View', 'Primitive Value Types Library']


def namespace_wrapper(ns, name):
    return "{" + NS[ns] + "}" + name


class SysMLParser:
    def __init__(self, model_path):
        self.tree = ET.parse(model_path)
        self.root = self.tree.getroot()
        self.model = self.root.find('uml:Model', NS).find('packagedElement', NS)

        self.package_map = {}
        self.association_map = {}
        self.activity_map = {}
        self.class_map = {}
        self.value_type_map = {}

        for value_type in self.root.find('xmi:Extension', NS).iter('element'):
            if value_type.get(namespace_wrapper('xmi', 'type')) == "uml:DataType":
                vid = value_type.get(namespace_wrapper('xmi', 'idref'))
                self.value_type_map[vid] = value_type.get("name")

        for package in self.model:
            if package.get('name') in SKIP_PACKAGE_NAMES:
                continue
            for element in package.iter('packagedElement'):
                element_id = element.get(namespace_wrapper('xmi', 'id'))
                element_type = element.get(namespace_wrapper('xmi', 'type'))
                if element_type == "uml:Package":
                    self.package_map[element_id] = element
                elif element_type == "uml:Class":
                    self.class_map[element_id] = element
                elif element_type == "uml:Activity":
                    self.activity_map[element_id] = element
                elif element_type == "uml:Association":
                    self.association_map[element_id] = element

    def get_class(self):
        class_attrib = {}
        for eid, element in self.class_map.items():
            element_name = element.get('name')
            class_attrib[element_name] = {}
            for attribute in element.iter('ownedAttribute'):
                attribute_type = attribute.get(namespace_wrapper('xmi', 'type'))
                attribute_name = attribute.get('name')
                if attribute_type == "uml:Property" and attribute_name is not None:
                    value_type_id = attribute.find("type").get(namespace_wrapper('xmi', "idref"))
                    class_attrib[element_name][attribute_name] = self.value_type_map[value_type_id]
            for attribute in element.iter('qualifier'):
                attribute_type = attribute.get(namespace_wrapper('xmi', 'type'))
                attribute_name = attribute.get('name')
                if attribute_type == "uml:Property" and attribute_name is not None:
                    value_type_id = attribute.find("type").get(namespace_wrapper('xmi', "idref"))
                    class_attrib[element_name][attribute_name] = self.value_type_map[value_type_id]
        return class_attrib

    def get_activity(self):
        activity_lst = []
        for eid, element in self.activity_map.items():
            element_name = element.get('name')
            if element_name != "EA_Activity1":
                activity_lst.append(element_name)
        return activity_lst

    def get_generalization(self):
        son_parent = {}

        for eid, element in self.class_map.items():
            element_name = element.get('name')
            for g in element.iter('generalization'):
                parent_id = g.get("general")
                parent_name = self.class_map[parent_id].get('name')
                if parent_name is None:
                    parent_name = self.activity_map[parent_id].get('name')
                son_parent[element_name] = parent_name

        for eid, element in self.activity_map.items():
            element_name = element.get('name')
            for g in element.iter('generalization'):
                parent_id = g.get("general")
                parent_name = self.class_map[parent_id].get('name')
                if parent_name is None:
                    parent_name = self.activity_map[parent_id].get('name')
                son_parent[element_name] = parent_name

        return son_parent

    def get_association(self):
        association_lst = []

        for eid, element in self.class_map.items():
            source_name = element.get('name')
            for attribute in element.iter('ownedAttribute'):
                rel_id = attribute.get('association')
                if rel_id is None:
                    continue
                rel_type = self.association_map[rel_id].get('name')
                target_id = attribute.find('type').get(namespace_wrapper('xmi', 'idref'))
                if target_id in self.class_map.keys():
                    target_name = self.class_map[target_id].get('name')
                elif target_id in self.activity_map.keys():
                    target_name = self.activity_map[target_id].get('name')
                else:
                    raise Exception("target element not found")
                association_lst.append([source_name, rel_type, target_name])

        for eid, element in self.activity_map.items():
            source_name = element.get('name')
            for attribute in element.iter('ownedAttribute'):
                rel_id = attribute.get('association')
                if rel_id is None:
                    continue
                rel_type = self.association_map[rel_id].get('name')
                target_id = attribute.find('type').get(namespace_wrapper('xmi', 'idref'))
                if target_id in self.class_map.keys():
                    target_name = self.class_map[target_id].get('name')
                elif target_id in self.activity_map.keys():
                    target_name = self.activity_map[target_id].get('name')
                else:
                    raise Exception("target element not found")
                association_lst.append([source_name, rel_type, target_name])

        return association_lst
