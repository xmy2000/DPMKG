package com.xmy.utils;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.apache.jena.ontology.*;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Resource;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.util.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class OWLReadUtils {
    private String OntologyName;
    private String OntologySourceName;
    private String OntologyNameSpace;
    private String OWLFilePath;
    private OntModel ontModel;

    public OWLReadUtils(String OWLFileName) throws FileNotFoundException {
        this.OntologyName = OWLFileName.split("\\(")[0];
        this.OntologySourceName = "http://www.semanticweb.org/xmy/ontologies/" + OntologyName;
        this.OntologyNameSpace = this.OntologySourceName + "#";
        this.OWLFilePath = System.getProperty("user.dir") + "\\src\\main\\resources\\data\\owl\\" + OWLFileName;
        this.ontModel = ModelFactory.createOntologyModel();
        this.ontModel.read(new FileInputStream(this.OWLFilePath), this.OntologySourceName, "RDF/XML");
    }

    public Map<String, String> traverseClassNameMap() {
        Map<String, String> nameMap = new HashMap<>();

        Set<OntClass> classes = ontModel.listClasses().toSet();
        for (OntClass ontClass : classes) {
            if (ontClass.getURI() != null) {
                String label = ontClass.getLabel("");
                String name = ontClass.getLocalName();
                switch (label) {
                    case "uml:Package" -> nameMap.put(name, "package");
                    case "uml:Class" -> nameMap.put(name, "class");
                    case "uml:Activity", "uml:Action" -> nameMap.put(name, "activity");
                    default -> nameMap.put(name, null);
                }
            }
        }

        return nameMap;
    }

    public Set<String> findSuperClass(String className) {
        Set<String> superClassName = new HashSet<>();
        OntClass ontClass = ontModel.getOntClass(OntologyNameSpace + className);
        Set<OntClass> superClasses = ontClass.listSuperClasses(true).toSet();
        for (OntClass superClass : superClasses) {
            if (superClass.getURI() != null) {
                superClassName.add(superClass.getLocalName());
            }
        }

        return superClassName;
    }

    public Map<String, List<String>> findObjectProperty(String className) {
        List<String> r_list = new ArrayList<>();
        List<String> c_list = new ArrayList<>();

        OntClass ontClass = ontModel.getOntClass(OntologyNameSpace + className);
        List<OntClass> superClasses = ontClass.listSuperClasses(true).toList();
        for (OntClass superClass : superClasses) {
            if (superClass.isRestriction()) {
                SomeValuesFromRestriction restriction = superClass.asRestriction().asSomeValuesFromRestriction();
                OntProperty property = restriction.getOnProperty();
                if (property.getRDFType().getLocalName().equals("ObjectProperty")) {
                    Resource value = restriction.getSomeValuesFrom();
                    r_list.add(property.getLocalName());
                    c_list.add(value.getLocalName());
                }
            }
        }

        Map<String, List<String>> map = new HashMap<>();
        map.put("relation", r_list);
        map.put("class", c_list);
        return map;
    }

    public Map<String, List<String>> findDataProperty(String className) {
        List<String> p_list = new ArrayList<>();
        List<String> t_list = new ArrayList<>();

        OntClass ontClass = ontModel.getOntClass(OntologyNameSpace + className);
        List<OntClass> superClasses = ontClass.listSuperClasses(true).toList();
        for (OntClass superClass : superClasses) {
            if (superClass.isRestriction()) {
                SomeValuesFromRestriction restriction = superClass.asRestriction().asSomeValuesFromRestriction();
                OntProperty property = restriction.getOnProperty();
                if (property.getRDFType().getLocalName().equals("DatatypeProperty")) {
                    Resource value = restriction.getSomeValuesFrom();
                    p_list.add(property.getLocalName());
                    t_list.add(value.getLocalName());
                }
            }
        }

        Map<String, List<String>> map = new HashMap<>();
        map.put("property", p_list);
        map.put("type", t_list);
        return map;
    }

    public static void main(String[] args) throws FileNotFoundException {
        OWLReadUtils utils = new OWLReadUtils("TLO(2023-08-28 11-15-38).owl");
        System.out.println(utils.findDataProperty("刀具清单"));
    }
}
