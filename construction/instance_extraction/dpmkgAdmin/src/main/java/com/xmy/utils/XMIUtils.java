package com.xmy.utils;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.w3c.dom.Document;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import java.io.File;
import java.io.IOException;
import java.util.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class XMIUtils {
    private String SysMLFileName;
    private Map<String, Node> id2class = new HashMap<>();
    private Map<String, Node> id2connector = new HashMap<>();
    private Map<String, String> id2dataType = new HashMap<>();
    private Map<String, Node> id2activityParameter = new HashMap<>();
    private Map<String, Node> id2controlFlow = new HashMap<>();
    private Map<String, Node> id2objectFlow = new HashMap<>();
    private Map<String, Node> id2activity = new HashMap<>();
    private Map<String, Node> id2objectNode = new HashMap<>();
    private Map<String, Node> id2package = new HashMap<>();

    public XMIUtils(String path) {
        this.SysMLFileName = path;
    }

    public Document readXMI() throws ParserConfigurationException, IOException, SAXException {
        String path = System.getProperty("user.dir") + "\\src\\main\\resources\\data\\sysml\\" + this.SysMLFileName;
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(new File(path));

        NodeList nodeList = doc.getElementsByTagName("packagedElement");
        for (int i = 0; i < nodeList.getLength(); i++) {
            Node item = nodeList.item(i);
            NamedNodeMap attributes = item.getAttributes();
            if (attributes == null) {
                continue;
            }
            if (attributes.getNamedItem("xmi:type").getNodeValue().equals("uml:Association")) {
                String id = attributes.getNamedItem("xmi:id").getNodeValue();
                id2connector.put(id, item);
            } else if (attributes.getNamedItem("xmi:type").getNodeValue().equals("uml:Class")) {
                String id = attributes.getNamedItem("xmi:id").getNodeValue();
                id2class.put(id, item);
            } else if (attributes.getNamedItem("xmi:type").getNodeValue().equals("uml:DataType")) {
                String id = attributes.getNamedItem("xmi:id").getNodeValue();
                String name = attributes.getNamedItem("name").getNodeValue();
                id2dataType.put(id, name);
            } else if (attributes.getNamedItem("xmi:type").getNodeValue().equals("uml:Activity")) {
                String id = attributes.getNamedItem("xmi:id").getNodeValue();
                id2activity.put(id, item);
            } else if (attributes.getNamedItem("xmi:type").getNodeValue().equals("uml:InstanceSpecification")) {
                String id = attributes.getNamedItem("xmi:id").getNodeValue();
                id2objectNode.put(id, item);
            } else if (attributes.getNamedItem("xmi:type").getNodeValue().equals("uml:Package")) {
                String id = attributes.getNamedItem("xmi:id").getNodeValue();
                id2package.put(id, item);
            }
        }

        NodeList nodes = doc.getElementsByTagName("node");
        for (int i = 0; i < nodes.getLength(); i++) {
            Node node = nodes.item(i);
            NamedNodeMap attributes = node.getAttributes();
            if (attributes == null || attributes.getNamedItem("xmi:type") == null) {
                continue;
            }
            if (attributes.getNamedItem("xmi:type").getNodeValue().equals("uml:ActivityParameterNode")) {
                String id = attributes.getNamedItem("xmi:id").getNodeValue();
                id2activityParameter.put(id, node);
            }
        }

        NodeList edges = doc.getElementsByTagName("edge");
        for (int i = 0; i < edges.getLength(); i++) {
            Node edge = edges.item(i);
            NamedNodeMap attributes = edge.getAttributes();
            if (attributes == null || attributes.getNamedItem("xmi:type") == null) {
                continue;
            }
            if (attributes.getNamedItem("xmi:type").getNodeValue().equals("uml:ControlFlow")) {
                String id = attributes.getNamedItem("xmi:id").getNodeValue();
                id2controlFlow.put(id, edge);
            } else if (attributes.getNamedItem("xmi:type").getNodeValue().equals("uml:ObjectFlow")) {
                String id = attributes.getNamedItem("xmi:id").getNodeValue();
                id2objectFlow.put(id, edge);
            }
        }

        return doc;
    }

    public Map<String, Integer> info() {
        Map<String, Integer> modelInfo = new HashMap<>();
        modelInfo.put("block", id2class.size());
        modelInfo.put("association", id2connector.size());
        modelInfo.put("dataType", id2dataType.size());
        modelInfo.put("activityParameter", id2activityParameter.size());
        modelInfo.put("controlFlow", id2controlFlow.size());
        modelInfo.put("objectFlow", id2objectFlow.size());
        modelInfo.put("activity", id2activity.size());
        modelInfo.put("objectNode", id2objectNode.size());
        modelInfo.put("package", id2package.size());
        return modelInfo;
    }
}
