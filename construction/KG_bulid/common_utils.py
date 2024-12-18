import re


def name_convert_to_camel(name: str) -> str:
    """下划线转驼峰(小驼峰)"""
    return re.sub(r'(_[a-z])', lambda x: x.group(1)[1].upper(), name)


def name_convert_to_snake(name: str) -> str:
    """驼峰转下划线"""
    if '_' not in name:
        name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
    else:
        raise ValueError(f'{name}字符中包含下划线，无法转换')
    return name.upper()


if __name__ == '__main__':
    print(name_convert_to_snake("hasFeature"))
