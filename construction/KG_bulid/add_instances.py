import pandas as pd
from Neo4jUtils import Neo4jUtils

neo4j_uri = "bolt://localhost:7687"
neo4j_username = "neo4j"
neo4j_password = "xxxxxx"
neo4j_utils = Neo4jUtils(neo4j_uri, neo4j_username, neo4j_password)

file_path = '../data/instances.xlsx'
part_df = pd.read_excel(file_path, sheet_name="工艺表").astype(str)
record_df = pd.read_excel(file_path, sheet_name="记录表").fillna('').astype(str)
quality_df = pd.read_excel(file_path, sheet_name="质量表").astype(str)
tool_df = pd.read_excel(file_path, sheet_name="刀具表").fillna('').astype(str)

neo4j_utils.delete_node_with_label("instance")
neo4j_utils.delete_node_with_label("activity_instance")

# 数字域
for row in range(len(part_df)):
    part_type = part_df.loc[row, '型号']
    blue_print_id = part_df.loc[row, '图号']
    process_id = part_df.loc[row, '工序']
    material = part_df.loc[row, '零件材料']
    program = part_df.loc[row, '数控程序']
    machine_tool = part_df.loc[row, '机床']

    part_name = '-'.join((part_type, blue_print_id))
    neo4j_utils.add_node("instance:digital", part_name)
    neo4j_utils.add_relationship(part_name, "Part", "INSTANCE_OF")

    process_name = '-'.join((part_type, blue_print_id, process_id))
    neo4j_utils.add_node("instance:digital", process_name)
    neo4j_utils.add_relationship(process_name, "工序", "INSTANCE_OF")

    neo4j_utils.add_node("instance:digital", material)
    neo4j_utils.add_relationship(material, "Material", "INSTANCE_OF")

    neo4j_utils.add_node("instance:digital", program)
    neo4j_utils.add_relationship(program, "NCProgram", "INSTANCE_OF")

    neo4j_utils.add_node("instance:digital", machine_tool)
    neo4j_utils.add_relationship(machine_tool, "MachineTool", "INSTANCE_OF")

    neo4j_utils.add_node("instance:digital", blue_print_id)
    neo4j_utils.add_relationship(blue_print_id, "Blueprint", "INSTANCE_OF")

    neo4j_utils.add_relationship(part_name, process_name, "HAS_PROCESS")
    neo4j_utils.add_relationship(part_name, material, "HAS_MATERIAL")
    neo4j_utils.add_relationship(process_name, blue_print_id, "INCLUDE")
    neo4j_utils.add_relationship(process_name, program, "INCLUDE")
    neo4j_utils.add_relationship(process_name, machine_tool, "HAS_EQUIPMENT")

for row in range(len(tool_df)):
    part_type = tool_df.loc[row, '零件名称']
    blue_print_id = tool_df.loc[row, '图号']
    process_id = tool_df.loc[row, '工序']
    tool_type = tool_df.loc[row, '刀具名称']
    tool_id = tool_df.loc[row, '刀具编号']

    tool_name = '-'.join((tool_type, tool_id))
    process_name = '-'.join((part_type, blue_print_id, process_id))
    neo4j_utils.add_node("instance:digital", tool_name)
    neo4j_utils.add_relationship(tool_name, "CuttingTool", "INSTANCE_OF")
    neo4j_utils.add_relationship(process_name, tool_name, "HAS_EQUIPMENT")

# 物理域
for row in range(len(record_df)):
    part_type = record_df.loc[row, '零件名称']
    blue_print_id = record_df.loc[row, '图号']
    part_id = record_df.loc[row, '零件ID']
    process_id = record_df.loc[row, '工序']
    process_type = record_df.loc[row, '加工类型']
    feature_type = record_df.loc[row, '特征']
    tool_id = record_df.loc[row, '刀具ID']
    if tool_id == '':
        continue
    tool_id = tool_id.replace('_', '-')
    p1 = record_df.loc[row, '进给量']
    p2 = record_df.loc[row, '转速']
    p3 = record_df.loc[row, '切深']
    parameter = {'type': process_type, '进给量': p1, '转速': p2, '切深': p3}
    w1 = record_df.loc[row, '是否破损']
    w2 = record_df.loc[row, '破损类型']
    w3 = record_df.loc[row, '磨损量']
    w4 = record_df.loc[row, '破损尺寸']
    wear_info = {'是否破损': w1, '破损类型': w2, '磨损量': w3, '破损尺寸': w4}

    execution_id = "加工" + str(row)
    neo4j_utils.add_node("activity_instance", execution_id)
    neo4j_utils.set_node_properties("activity_instance", execution_id, parameter)
    neo4j_utils.add_relationship(execution_id, "ProcessExecution", "INSTANCE_OF")

    test_id = "刀具检测" + str(row)
    neo4j_utils.add_node("activity_instance", test_id)
    neo4j_utils.set_node_properties("activity_instance", test_id, wear_info)
    neo4j_utils.add_relationship(test_id, "FeedbackControl", "INSTANCE_OF")

    part_name = '-'.join((part_type, blue_print_id))
    part_name_ins = '-'.join((part_type, blue_print_id, part_id))
    neo4j_utils.add_node("instance:physical", part_name_ins)
    neo4j_utils.add_relationship(part_name_ins, part_name, "INSTANCE_OF")

    feature_name = '-'.join((part_type, blue_print_id, process_id, feature_type))
    neo4j_utils.add_node("instance:physical", feature_name)
    neo4j_utils.add_relationship(feature_name, "Feature", "INSTANCE_OF")

    tool_name_ins = '-'.join((part_name_ins, process_id, tool_id))
    tool_select = tool_df[(tool_df['零件名称'] == part_type) &
                          (tool_df['图号'] == blue_print_id) &
                          (tool_df['工序'] == process_id) &
                          (tool_df['刀号'] == tool_id.split('-')[0].strip())]
    tool_type = tool_select.iloc[0, 4]
    tool_type_id = tool_select.iloc[0, 5]
    tool_name = '-'.join((tool_type, tool_type_id))
    neo4j_utils.add_node("instance:physical", tool_name_ins)
    neo4j_utils.add_relationship(tool_name_ins, tool_name, "INSTANCE_OF")

    neo4j_utils.add_relationship(execution_id, part_name_ins, "HAS_MATERIAL_OUTPUT")
    neo4j_utils.add_relationship(execution_id, feature_name, "HAS_MATERIAL_OUTPUT")
    neo4j_utils.add_relationship(tool_name_ins, execution_id, "SUPPORT")
    neo4j_utils.add_relationship(part_name_ins, feature_name, "HAS_FEATURE")
    neo4j_utils.add_relationship(tool_name_ins, feature_name, "WORK_ON")
    neo4j_utils.add_relationship(test_id, tool_name_ins, "IS_ABOUT")

for row in range(len(quality_df)):
    part_type = quality_df.loc[row, '零件名称']
    blue_print_id = quality_df.loc[row, '图号']
    part_id = quality_df.loc[row, '零件ID']
    process_id = quality_df.loc[row, '工序']
    feature_type = quality_df.loc[row, '特征']
    process_type = quality_df.loc[row, '加工类型']
    test_result = quality_df.loc[row, '粗糙度']
    quality_info = {'加工类型': process_type, '粗糙度': test_result}

    part_name = '-'.join((part_type, blue_print_id))
    part_name_ins = '-'.join((part_type, blue_print_id, part_id))
    neo4j_utils.add_node("instance:physical", part_name_ins)
    neo4j_utils.add_relationship(part_name_ins, part_name, "INSTANCE_OF")

    feature_name = '-'.join((part_type, blue_print_id, process_id, feature_type))
    neo4j_utils.add_node("instance:physical", feature_name)
    neo4j_utils.add_relationship(feature_name, "Feature", "INSTANCE_OF")

    test_id = '-'.join(("零件检测", part_type, blue_print_id, process_id, feature_type))
    neo4j_utils.add_node("activity_instance", test_id)
    neo4j_utils.set_node_properties("activity_instance", test_id, quality_info)
    neo4j_utils.add_relationship(test_id, "FeedbackControl", "INSTANCE_OF")

    neo4j_utils.add_relationship(part_name_ins, feature_name, "HAS_FEATURE")
    neo4j_utils.add_relationship(test_id, feature_name, "IS_ABOUT")
