import pandas as pd
import sys

from ontology_utils import OntUtils
from neo4jUtils2 import Neo4jUtils
from common_utils import name_convert_to_snake

ont_utils = OntUtils("file://../Ontology/ProcessKonwledegBase.rdf")
neo4j_utils = Neo4jUtils("bolt://localhost:7687", "neo4j", "xxxxxx")

neo4j_utils.deleteAll()

machine = pd.read_csv("../data/machine.csv")
material = pd.read_csv("../data/material.csv")
part = pd.read_csv("../data/part.csv")
tool = pd.read_csv("../data/tool_new.csv")
tool.fillna(value="unknow", inplace=True)


class EntityProcess:
    def __init__(self, entity, ont_utils, neo4j_utils):
        self.entity = entity
        self.ont_utils = ont_utils
        self.neo4j_utils = neo4j_utils
        self.father, self.object_property, self.datatype_property = ont_utils.parseClass(entity)

    def base_extraction(self, df):
        for i in range(len(df)):
            id = df.iloc[i]["ID"]
            name = df.iloc[i]["name"]
            self.neo4j_utils.addNode(id, name, self.entity)
            for (p, t) in self.datatype_property:
                value = df.iloc[i][p]
                self.neo4j_utils.addNodeProperty(name, p, value)


machine_process = EntityProcess("Machine", ont_utils, neo4j_utils)
machine_process.base_extraction(machine)
material_process = EntityProcess("Material", ont_utils, neo4j_utils)
material_process.base_extraction(material)
tool_process = EntityProcess("Tool", ont_utils, neo4j_utils)
tool_process.base_extraction(tool)


class PartProcess(EntityProcess):
    def __init__(self, entity, ont_utils, neo4j_utils):
        super(PartProcess, self).__init__(entity, ont_utils, neo4j_utils)
        self.path = None

    def part_extraction(self, df):
        self.base_extraction(df)

        for i in range(len(df)):
            id = df.iloc[i]["ID"]
            name = df.iloc[i]["name"]
            n1 = name.split("_")[0]
            n2 = name.split("_")[1]
            self.path = "../data/" + n1 + "/" + n2 + "/"
            for (p, v) in self.object_property:
                if p == "hasProcess":
                    route_id = str(id) + "_" + str(df.iloc[i][v + "_ID"])
                    self.neo4j_utils.addNode(route_id, v + route_id, v)
                    self.neo4j_utils.addRelationById(self.entity, id, v, route_id, name_convert_to_snake(p))

                    file_path = self.path + "工序.csv"
                    procedure = pd.read_csv(file_path)
                    procedure = procedure[procedure["工艺路线_ID"] == df.iloc[i][v + "_ID"]]
                    self.procedure_process(procedure, route_id)
                elif p == "hasFeatures":
                    file_path = self.path + v.lower() + ".csv"
                    feature = pd.read_csv(file_path)
                    self.feature_process(feature, id)
                else:
                    target_id = df.iloc[i][v + "_ID"]
                    self.neo4j_utils.addRelationById(self.entity, id, v, target_id, name_convert_to_snake(p))

        for i in range(len(df)):  # 特征和工艺交互的关系要等元素全部建完后才能加
            part_id = df.iloc[i]["ID"]
            name = df.iloc[i]["name"]
            n1 = name.split("_")[0]
            n2 = name.split("_")[1]
            self.path = "../data/" + n1 + "/" + n2 + "/"

            file_path = self.path + "feature.csv"
            feature_df = pd.read_csv(file_path)
            for j in range(len(feature_df)):
                feature_id = str(part_id) + "_" + str(feature_df.iloc[j]["ID"])
                step_id = feature_df.iloc[j]["工步_ID"]
                if not pd.isnull(step_id):
                    step_id_list = step_id.split(";")
                    for si in step_id_list:
                        sid = self.neo4j_utils.findID(feature_id) + "_" + si
                        self.neo4j_utils.addRelationById("Feature", feature_id, "工步", sid,
                                                         name_convert_to_snake("isProcessedBy"))

    def procedure_process(self, df, route_id):
        tool_df = pd.read_csv(self.path + "刀具清单.csv")

        for i in range(len(df)):
            id = str(route_id) + "_" + str(df.iloc[i]["ID"])
            name = df.iloc[i]["name"]

            self.neo4j_utils.addNode(id, name, "工序")

            self.neo4j_utils.addRelationById("工艺路线", route_id, "工序", id, name_convert_to_snake("hasComponent"))

            machine_id = df.iloc[i]["machine_ID"]
            if not pd.isnull(machine_id):
                machine_id = int(machine_id)
                self.neo4j_utils.addRelationById("工序", id, "Machine", machine_id,
                                                 name_convert_to_snake("useMachine"))

            tool_list_id = df.iloc[i]["刀具清单_ID"]
            if not pd.isnull(tool_list_id):
                tool_df = tool_df[tool_df["ID"] == int(tool_list_id)]
                tool_list_id = str(id) + "_" + str(int(tool_list_id))
                self.neo4j_utils.addNode(tool_list_id, "刀具清单", "刀具清单")
                self.neo4j_utils.addRelationById("工序", id, "刀具清单", tool_list_id,
                                                 name_convert_to_snake("useToolList"))
                for j in range(len(tool_df)):
                    self.neo4j_utils.addRelationByIdAndName("刀具清单", tool_list_id, "Tool",
                                                            tool_df.iloc[j]["tool_name"],
                                                            name_convert_to_snake("include"))

            # 处理工步
            step_df = pd.read_csv(self.path + "工步.csv")
            step_df = step_df[step_df["工艺路线_ID"] == int(route_id.split("_")[-1])]
            step_df = step_df[step_df["工序_ID"] == int(id.split("_")[-1])]
            self.step_process(step_df, id)

    def step_process(self, df, procedure_id):
        parameter_df = pd.read_csv(self.path + "parameter.csv")
        for i in range(len(df)):
            id = str(procedure_id) + "_" + str(df.iloc[i]["ID"])
            precision = df.iloc[i]["Precision"]
            parameter_id = df.iloc[i]["Parameter_ID"]
            tool_name = df.iloc[i]["tool_name"]

            self.neo4j_utils.addNode(id, str(df.iloc[i]["ID"]), "工步")
            self.neo4j_utils.addRelationById("工序", procedure_id, "工步", id, name_convert_to_snake("hasComponent"))
            self.neo4j_utils.addNodePropertyById("工步", id, "Precision", precision)
            self.neo4j_utils.addRelationByIdAndName("工步", id, "Tool",
                                                    tool_name,
                                                    name_convert_to_snake("useTool"))
            parameter = parameter_df[parameter_df["ID"] == parameter_id]
            self.neo4j_utils.addNodePropertyById("工步", id, "feed", parameter.iloc[0]["feed"])
            self.neo4j_utils.addNodePropertyById("工步", id, "rotate", parameter.iloc[0]["rotate"])
            self.neo4j_utils.addNodePropertyById("工步", id, "depth", parameter.iloc[0]["depth"])

    def feature_process(self, df, part_id):
        for i in range(len(df)):
            id = str(part_id) + "_" + str(df.iloc[i]["ID"])
            name = df.iloc[i]["type"]
            self.neo4j_utils.addNode(id, name, "Feature")
            self.neo4j_utils.addRelationById(self.entity, part_id, "Feature", id, name_convert_to_snake("hasFeatures"))

            # 添加feature类的关系和属性
            father, object_property, datatype_property = self.ont_utils.parseClass("Feature")
            for (p, t) in datatype_property:
                if p == "ID" or p == "name":
                    continue
                value = df.iloc[i][p]
                self.neo4j_utils.addNodePropertyById("Feature", id, p, value)
            for (p, v) in object_property:
                if p == "hasGeometricData":
                    file_path = self.path + v.lower() + ".csv"
                    design_data = pd.read_csv(file_path)

                    design_data_id = df.iloc[i][v + "_ID"]
                    if not pd.isnull(design_data_id):
                        ids = str(design_data_id).split(";")
                        for design_id in ids:
                            self.process_design_data(design_data, id, design_id)

    def process_design_data(self, df, feature_id, design_id):
        id = str(feature_id) + "_" + design_id
        name = df.iloc[int(design_id) - 1]["name"]
        self.neo4j_utils.addNode(id, name, "DesignData")
        father, object_property, datatype_property = self.ont_utils.parseClass("DesignData")
        for (p, t) in datatype_property:
            if p == "ID" or p == "name":
                continue
            value = df.iloc[int(design_id) - 1][p]
            self.neo4j_utils.addNodePropertyById("DesignData", id, p, value)
        self.neo4j_utils.addRelationById("Feature", feature_id, "DesignData", id,
                                         name_convert_to_snake("hasGeometricData"))


part_process = PartProcess("Part", ont_utils, neo4j_utils)
part_process.part_extraction(part)
