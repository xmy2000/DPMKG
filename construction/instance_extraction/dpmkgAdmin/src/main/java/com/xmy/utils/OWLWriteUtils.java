package com.xmy.utils;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.apache.jena.ontology.*;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Resource;
import org.apache.jena.vocabulary.XSD;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class OWLWriteUtils {
    private String OntologyName;
    private String OntologySourceName;
    private String OntologyNameSpace;
    private String OWLFilePath;
    private OntModel ontModel;

    private static final Map<String, Resource> datatype = new HashMap<>() {{
        put("Time", XSD.dateTime);
        put("File", XSD.token);
        put("String", XSD.xstring);
        put("Boolean", XSD.xboolean);
        put("Real", XSD.xdouble);
        put("Integer", XSD.integer);
    }};

    public OWLWriteUtils(String ontName) throws IOException {
        this.OntologyName = ontName;
        this.OntologySourceName = "http://www.semanticweb.org/xmy/ontologies/" + ontName;
        this.OntologyNameSpace = this.OntologySourceName + "#";
        this.OWLFilePath = System.getProperty("user.dir") + "\\src\\main\\resources\\data\\owl\\"
                + ontName + "(" + CommonUtils.getDateTime() + ").owl";
        String baseFilePath = System.getProperty("user.dir") + "\\src\\main\\resources\\data\\owl\\base.owl";
        this.ontModel = ModelFactory.createOntologyModel();
        this.ontModel.read(new FileInputStream(baseFilePath), this.OntologySourceName, "RDF/XML");
        saveOntModel();
    }

    public void saveOntModel() throws IOException {
        //输出owl文件到文件系统
        FileOutputStream fileOS = new FileOutputStream(OWLFilePath);
        ontModel.write(fileOS, "RDF/XML");
        fileOS.close();
    }

    public void addClass(String className) throws IOException {
        className = CommonUtils.classNameInspect(className);

        OntClass ontClass = ontModel.createClass(OntologyNameSpace + className);
        saveOntModel();
    }

    public void addSubClass(String father, String son) throws IOException {
        father = CommonUtils.classNameInspect(father);
        son = CommonUtils.classNameInspect(son);

        OntClass fatherClass = ontModel.createClass(OntologyNameSpace + father);
        OntClass sonClass = ontModel.createClass(OntologyNameSpace + son);
        fatherClass.addSubClass(sonClass);
        saveOntModel();
    }

    public void addDataProperty(String cls, String value, String dataType) throws IOException {
        cls = CommonUtils.classNameInspect(cls);
        value = CommonUtils.classNameInspect(value);

        OntClass ontClass = ontModel.createClass(OntologyNameSpace + cls);
        DatatypeProperty datatypeProperty = ontModel.createDatatypeProperty(OntologyNameSpace + value);
        SomeValuesFromRestriction restriction = ontModel.createSomeValuesFromRestriction(null, datatypeProperty, datatype.get(dataType));
        ontClass.addSuperClass(restriction);
        saveOntModel();
    }

    public void addObjectProperty(String source, String relationshipType, String target) throws IOException {
        source = CommonUtils.classNameInspect(source);
        target = CommonUtils.classNameInspect(target);
        relationshipType = CommonUtils.classNameInspect(relationshipType);

        OntClass sourceClass = ontModel.createClass(OntologyNameSpace + source);
        OntClass targetClass = ontModel.createClass(OntologyNameSpace + target);
        ObjectProperty objectProperty = ontModel.createObjectProperty(OntologyNameSpace + relationshipType);
        SomeValuesFromRestriction restriction = ontModel.createSomeValuesFromRestriction(null, objectProperty, targetClass);
        sourceClass.addSuperClass(restriction);
        saveOntModel();
    }

    public void addClassLabel(String className, String label) throws IOException {
        className = CommonUtils.classNameInspect(className);

        OntClass ontClass = ontModel.createClass(OntologyNameSpace + className);
        ontClass.addLabel(label, "");
        saveOntModel();
    }

    public Map<String, Integer> info() {
        Map<String, Integer> modelInfo = new HashMap<>();
        modelInfo.put("class", ontModel.listClasses().toList().size());
        modelInfo.put("objectProperty", ontModel.listObjectProperties().toList().size());
        modelInfo.put("datatypeProperty", ontModel.listDatatypeProperties().toList().size());
        modelInfo.put("restriction", ontModel.listRestrictions().toList().size());
        return modelInfo;
    }

    public static void main(String[] args) throws IOException {
        OWLWriteUtils utils = new OWLWriteUtils("TLO");
        utils.addClass("c1");
        utils.addSubClass("c1", "c2");
        utils.addDataProperty("c2", "data", "String");
        utils.addObjectProperty("c1", "TO", "c2");
        utils.addClassLabel("c2", "label");
    }
}
