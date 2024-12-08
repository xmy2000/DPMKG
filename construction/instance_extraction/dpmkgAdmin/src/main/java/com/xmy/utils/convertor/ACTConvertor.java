package com.xmy.utils.convertor;

import com.xmy.utils.OWLWriteUtils;
import com.xmy.utils.XMIUtils;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.w3c.dom.Document;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import javax.xml.parsers.ParserConfigurationException;
import java.io.IOException;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ACTConvertor {
    private XMIUtils xmiUtils;
    private OWLWriteUtils owlWriteUtils;

    public void convert() throws ParserConfigurationException, IOException, SAXException {
        Document doc = xmiUtils.readXMI();
        NodeList activityList = doc.getElementsByTagName("packagedElement");

        for (int i = 0; i < activityList.getLength(); i++) {
            Node activity = activityList.item(i);
            NamedNodeMap attributes = activity.getAttributes();
            Node activityType = attributes.getNamedItem("xmi:type");
            Node activityName = attributes.getNamedItem("name");
            if (activityType == null ||
                    activityName == null ||
                    !activityType.getNodeValue().equals("uml:Activity") ||
                    activityName.getNodeValue().startsWith("EA_Activity")
            ) {
                // 不是活动节点则跳过
                continue;
            }
            // 活动映射的类在BDD中已经添加，因此只加标签
            owlWriteUtils.addClassLabel(activityName.getNodeValue(), "uml:Activity");
            NodeList childNodes = activity.getChildNodes();
            for (int j = 0; j < childNodes.getLength(); j++) {
                Node child = childNodes.item(j);
                String childType = child.getNodeName();
                if (childType.equals("node")) {
                    String nodeType = child.getAttributes().getNamedItem("xmi:type").getNodeValue();
                    // [uml:ActivityFinalNode, uml:InitialNode, uml:DecisionNode, uml:FlowFinalNode, uml:MergeNode,
                    // uml:ActivityParameterNode, uml:Action, uml:CallBehaviorAction, uml:ForkNode]
                    if (nodeType.equals("uml:Action")) {
                        String childName = child.getAttributes().getNamedItem("name").getNodeValue();
                        String parentName = activity.getParentNode().getAttributes().getNamedItem("name").getNodeValue();
                        owlWriteUtils.addSubClass(parentName, childName);
                        owlWriteUtils.addObjectProperty(activityName.getNodeValue(), "include", childName);
                        owlWriteUtils.addClassLabel(childName, "uml:Action");
                        findActionParameter(child, null);
                    } else if (nodeType.equals("uml:CallBehaviorAction")) {
                        NodeList childChildNodes = child.getChildNodes();
                        for (int k = 0; k < childChildNodes.getLength(); k++) {
                            Node behavior = childChildNodes.item(k);
                            if (behavior.getNodeName().equals("behavior")) {
                                String callId = behavior.getAttributes().getNamedItem("xmi:idref").getNodeValue();
                                Node callActivity = xmiUtils.getId2activity().get(callId);
                                String callName = callActivity.getAttributes().getNamedItem("name").getNodeValue();
                                owlWriteUtils.addObjectProperty(activityName.getNodeValue(), "call", callName);
                                findActionParameter(child, callName);
                            }
                        }
                    }
                }
            }
        }
        System.out.println("==========ACT图解析完成==========");
    }

    public void findActionParameter(Node action, String callName) throws IOException {
        NodeList childNodes = action.getChildNodes();
        for (int i = 0; i < childNodes.getLength(); i++) {
            Node child = childNodes.item(i);
            if (child.getNodeName().equals("input") || child.getNodeName().equals("argument")) {
                process(action, child, callName, "in");
            } else if (child.getNodeName().equals("output")) {
                process(action, child, callName, "out");
            }
        }
    }

    public void process(Node action, Node child, String callName, String direction) throws IOException {
        NodeList childChildNodes = child.getChildNodes();
        String flowDirection = "";
        String relationship = "";
        if (direction.equals("in")) {
            flowDirection = "source";
            relationship = "hasInput";
        } else if (direction.equals("out")) {
            flowDirection = "target";
            relationship = "hasOutput";
        }

        for (int j = 0; j < childChildNodes.getLength(); j++) {
            if (childChildNodes.item(j).getAttributes() == null) {
                continue;
            }
            String flowId = childChildNodes.item(j).getAttributes().getNamedItem("xmi:idref").getNodeValue();
            Node objectFlow = xmiUtils.getId2objectFlow().get(flowId);
            if (objectFlow == null) {
                continue;
            }
            String activityParameterId = objectFlow.getAttributes().getNamedItem(flowDirection).getNodeValue();
            Node activityParameter = xmiUtils.getId2activityParameter().get(activityParameterId);
            if (activityParameter != null) {
                NodeList inputActivityParameterChildNodes = activityParameter.getChildNodes();
                for (int k = 0; k < inputActivityParameterChildNodes.getLength(); k++) {
                    Node type = inputActivityParameterChildNodes.item(k);
                    if (type.getNodeName().equals("type")) {
                        String nodeId = type.getAttributes().getNamedItem("xmi:idref").getNodeValue();
                        addData(nodeId, callName, relationship, action);
                    }
                }
            } else {
                Node objectNode = xmiUtils.getId2objectNode().get(activityParameterId);
                if (objectNode == null || objectNode.getAttributes().getNamedItem("classifier") == null) {
                    continue;
                }
                String classifierId = objectNode.getAttributes().getNamedItem("classifier").getNodeValue();
                addData(classifierId, callName, relationship, action);
            }
        }
    }

    public void addData(String classifierId, String callName, String relationship, Node action) throws IOException {
        Node node = xmiUtils.getId2class().get(classifierId);
        if (node == null) {
            return;
        }
        if (callName != null) {
            owlWriteUtils.addObjectProperty(
                    callName,
                    relationship,
                    node.getAttributes().getNamedItem("name").getNodeValue());
        } else {
            owlWriteUtils.addObjectProperty(
                    action.getAttributes().getNamedItem("name").getNodeValue(),
                    relationship,
                    node.getAttributes().getNamedItem("name").getNodeValue());
        }
    }
}
