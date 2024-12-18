import owlready2


class OntUtils:
    def __init__(self, path):
        self.ont = owlready2.get_ontology(path).load()
        print("Ontology load successfully!")

    def parseClass(self, name):
        cls = self.ont[name]
        superClasses = cls.is_a
        father = []
        object_property = []
        datatype_property = []
        for s in superClasses:
            if type(s) == owlready2.entity.ThingClass:
                father.append(s.name)
            elif type(s) == owlready2.class_construct.Restriction:
                prop = s.property
                value = s.value
                if type(prop) == owlready2.prop.ObjectPropertyClass:
                    object_property.append((prop._name, value.name))
                elif type(prop) == owlready2.prop.DataPropertyClass:
                    datatype_property.append((prop._name, str(value)))
        return father, object_property, datatype_property
