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
public class BDDConvertor {
    private XMIUtils xmiUtils;
    private OWLWriteUtils owlWriteUtils;

    public void convert() throws IOException, ParserConfigurationException, SAXException {
        Document doc = xmiUtils.readXMI();
        NodeList packagedElementList = doc.getElementsByTagName("packagedElement");
        for (int i = 0; i < packagedElementList.getLength(); i++) {
            Node item = packagedElementList.item(i);
            NamedNodeMap attributes = item.getAttributes();
            Node itemType = attributes.getNamedItem("xmi:type");
            Node itemName = attributes.getNamedItem("name");
            if (itemName != null &&
                    (itemName.getNodeValue().equals("Model") ||
                            itemName.getNodeValue().equals("EA_PrimitiveTypes_Package") ||
                            itemName.getNodeValue().equals("Primitive Value Types Library")
                    )
            ) {
                // 元素类型为Model或数值类型库，则跳过该元素
                continue;
            } else if (itemName != null && itemType.getNodeValue().equals("uml:Package")) {
                // 处理包元素
                owlWriteUtils.addClass(itemName.getNodeValue());
                owlWriteUtils.addClassLabel(itemName.getNodeValue(), "uml:Package");
                processPackage(item, itemName.getNodeValue());
            } else if (itemName != null && itemType.getNodeValue().equals("uml:Class")) {
                // 处理块元素
                owlWriteUtils.addClass(itemName.getNodeValue());
                owlWriteUtils.addClassLabel(itemName.getNodeValue(), "uml:Class");
                processBlock(item, itemName.getNodeValue());
            }
//            else if (itemType.getNodeValue().equals("uml:Association")) {
//                // 处理关联关系元素
//            } else if (itemName != null && itemType.getNodeValue().equals("uml:DataType")) {
//                // 处理数值类型元素
//            }
        }

        System.out.println("==========BDD图解析完成==========");
    }

    public void processPackage(Node pack, String name) throws IOException {
        NodeList childNodes = pack.getChildNodes();
        for (int i = 0; i < childNodes.getLength(); i++) {
            NamedNodeMap attributes = childNodes.item(i).getAttributes();
            if (attributes != null) {
                Node itemType = attributes.getNamedItem("xmi:type");
                Node itemName = attributes.getNamedItem("name");
                if (itemType == null || itemName == null) {
                    continue;
                }
                switch (itemType.getNodeValue()) {
                    case "uml:Package" -> {
                        owlWriteUtils.addSubClass(name, itemName.getNodeValue());
                    }
                    case "uml:Class" -> {
                        owlWriteUtils.addSubClass(name, itemName.getNodeValue());
                    }
                    case "uml:Activity" -> {
                        if (!itemName.getNodeValue().startsWith("EA_Activity")) {
                            owlWriteUtils.addSubClass(name, itemName.getNodeValue());
                        }
                    }
                }
            }
        }
    }

    public void processBlock(Node block, String blockName) throws IOException {
        NodeList childNodes = block.getChildNodes();
        for (int i = 0; i < childNodes.getLength(); i++) {
            Node item = childNodes.item(i);
            NamedNodeMap attributes = item.getAttributes();
            if (attributes == null) {
                continue;
            }
            String nodeType = item.getNodeName();

            // 处理block的分区，映射为关系
            // 将block的value映射为datatype，将part映射为objectProperty
            if (nodeType.equals("ownedAttribute") &&
                    attributes.getNamedItem("aggregation") != null &&
                    attributes.getNamedItem("aggregation").getNodeValue().equals("composite")) {
                NodeList childNodes1 = item.getChildNodes();
                for (int j = 0; j < childNodes1.getLength(); j++) {
                    Node item1 = childNodes1.item(j);
                    String nodeName = item1.getNodeName();
                    if (nodeName.equals("type")) {
                        Node idref = item1.getAttributes().getNamedItem("xmi:idref");
                        if (idref != null) {
                            String id = idref.getNodeValue();
                            String datatype = this.xmiUtils.getId2dataType().get(id);
                            if (datatype != null) {
                                // 处理value分区
                                String itemName = attributes.getNamedItem("name").getNodeValue();
                                owlWriteUtils.addDataProperty(blockName, itemName, datatype);
                            } else {
                                // 处理part分区
                                Node classType = this.xmiUtils.getId2class().get(id);
                                String name = classType.getAttributes().getNamedItem("name").getNodeValue();
                                owlWriteUtils.addObjectProperty(blockName, "hasPart", name);
                            }
                        } else {
                            // 处理部分异常模块
                            String href = item1.getAttributes().getNamedItem("href").getNodeValue();
                            String type = href.split("#")[1];
                            String itemName = attributes.getNamedItem("name").getNodeValue();
                            owlWriteUtils.addDataProperty(blockName, itemName, type);
                        }
                    }
                }
            }

            // 处理关联关系
            // association="EAID_2447C5D1_41F7_4d81_BCD1_A65B20247DA4" -> connector -> name
            // xmi:idref="EAID_F1A4BD42_8448_407e_9F5E_8DDC4448DE15" -> class -> name
            if (nodeType.equals("ownedAttribute") &&
                    attributes.getNamedItem("aggregation") != null &&
                    attributes.getNamedItem("aggregation").getNodeValue().equals("none")) {
                String relationshipTypeId = attributes.getNamedItem("association").getNodeValue();
                String classId = "";
                NodeList childNodes1 = item.getChildNodes();
                for (int j = 0; j < childNodes1.getLength(); j++) {
                    Node item1 = childNodes1.item(j);
                    String nodeName = item1.getNodeName();
                    if (nodeName.equals("type")) {
                        Node idref = item1.getAttributes().getNamedItem("xmi:idref");
                        classId = idref.getNodeValue();
                        break;
                    }
                }
                String relationshipName = "";
                Node name = xmiUtils.getId2connector().get(relationshipTypeId).getAttributes().getNamedItem("name");
                if (name == null) {
                    relationshipName = "hasRelation";
                } else {
                    relationshipName = name.getNodeValue();
                }
                String className = xmiUtils.getId2class().get(classId).getAttributes().getNamedItem("name").getNodeValue();
                owlWriteUtils.addObjectProperty(blockName, relationshipName, className);
            }

            // 处理泛化关系
            if (nodeType.equals("generalization")) {
                String generalId = attributes.getNamedItem("general").getNodeValue();
                Node generalNode = xmiUtils.getId2class().get(generalId);
                String generalName = generalNode.getAttributes().getNamedItem("name").getNodeValue();
                owlWriteUtils.addSubClass(generalName, blockName);
            }
        }
    }

    public static void main(String[] args) throws IOException, ParserConfigurationException, SAXException {
        XMIUtils xmiUtils1 = new XMIUtils("sysml.xml");
        OWLWriteUtils owlWriteUtils1 = new OWLWriteUtils("TLO");
        BDDConvertor convertor = new BDDConvertor(xmiUtils1, owlWriteUtils1);
        convertor.convert();
    }
}
