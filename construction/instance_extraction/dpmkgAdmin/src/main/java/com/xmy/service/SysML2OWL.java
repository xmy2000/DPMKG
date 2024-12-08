package com.xmy.service;

import com.xmy.utils.OWLWriteUtils;
import com.xmy.utils.XMIUtils;
import com.xmy.utils.convertor.ACTConvertor;
import com.xmy.utils.convertor.BDDConvertor;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.xml.sax.SAXException;

import javax.xml.parsers.ParserConfigurationException;
import java.io.IOException;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SysML2OWL {
    private String SysMLFileName;
    private String OntologyName;
    private XMIUtils xmiUtils;
    private OWLWriteUtils owlWriteUtils;

    public SysML2OWL(String SysMLFileName, String OntologyName) throws IOException {
        this.SysMLFileName = SysMLFileName;
        this.OntologyName = OntologyName;
        this.xmiUtils = new XMIUtils(SysMLFileName);
        this.owlWriteUtils = new OWLWriteUtils(OntologyName);
    }

    public void convert() throws IOException, ParserConfigurationException, SAXException {
        BDDConvertor bddConvertor = new BDDConvertor(xmiUtils, owlWriteUtils);
        ACTConvertor actConvertor = new ACTConvertor(xmiUtils, owlWriteUtils);

        bddConvertor.convert();
        actConvertor.convert();

        Map<String, Integer> sysmlInfo = xmiUtils.info();
        Map<String, Integer> ontInfo = owlWriteUtils.info();
        System.out.println("==========转换完成==========");
        System.out.println("解析package: " + sysmlInfo.get("package"));
        System.out.println("解析block: " + sysmlInfo.get("block"));
        System.out.println("解析association: " + sysmlInfo.get("association"));
        System.out.println("解析dataType: " + sysmlInfo.get("dataType"));
        System.out.println("解析activity: " + sysmlInfo.get("activity"));
        System.out.println("解析关联关系: " +
                (sysmlInfo.get("association") + sysmlInfo.get("controlFlow") + sysmlInfo.get("objectFlow")));
        System.out.println(" ");
        System.out.println("生成class: " + ontInfo.get("class"));
        System.out.println("生成objectProperty: " + ontInfo.get("objectProperty"));
        System.out.println("生成datatypeProperty: " + ontInfo.get("datatypeProperty"));
        System.out.println("生成restriction: " + ontInfo.get("restriction"));
    }

    public static void main(String[] args) throws IOException, ParserConfigurationException, SAXException {
        String sysml = "sysml.xml";
        String ont = "TLO";
        SysML2OWL c = new SysML2OWL(sysml, ont);
        c.convert();
    }
}
