import xml.etree.ElementTree as ET


def parse_tcx_coordinates(tcx_file_path):
    """
    解析TCX文件并返回经纬度坐标数组

    参数:
        tcx_file_path (str): TCX文件路径

    返回:
        list: 包含(longitude, latitude)元组的列表，如果没有坐标则返回空列表
    """
    # 定义TCX文件的命名空间
    namespaces = {
        'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
        'ns2': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
        'ns3': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'
    }

    coordinates = []

    try:
        # 解析XML文件
        tree = ET.parse(tcx_file_path)
        root = tree.getroot()

        # 查找所有的Trackpoint节点
        for trackpoint in root.findall('.//ns:Trackpoint', namespaces):
            position = trackpoint.find('ns:Position', namespaces)
            if position is not None:
                lat = position.find('ns:LatitudeDegrees', namespaces)
                lon = position.find('ns:LongitudeDegrees', namespaces)
                if lat is not None and lon is not None:
                    coordinates.append((float(lat.text), float(lon.text)))

    except ET.ParseError as e:
        print(f"XML解析错误: {e}")
    except Exception as e:
        print(f"处理文件时出错: {e}")

    return coordinates


# 使用示例
if __name__ == "__main__":
    coords = parse_tcx_coordinates("/path/to/tcx")
    print(f"找到 {len(coords)} 个坐标点")
    for i, (lat, lon) in enumerate(coords[:5], 1):  # 只打印前5个作为示例
        print(f"坐标点 {i}: 经度={lon}, 纬度={lat}")
