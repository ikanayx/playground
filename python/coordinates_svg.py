import xml.etree.ElementTree as ET
from xml.dom import minidom
import math
import numpy as np
from scipy.interpolate import splprep, splev

from tcx_parse import parse_tcx_coordinates


def simplify_coordinates(coordinates, tolerance=0.0001, highest_quality=False):
    """
    使用Douglas-Peucker算法简化轨迹坐标点

    参数:
        coordinates: 原始坐标列表 [(lat1, lon1), (lat2, lon2), ...]
        tolerance: 简化容忍度（单位与坐标相同）
        highest_quality: 是否使用高质量简化（较慢但更精确）

    返回:
        简化后的坐标列表
    """
    if len(coordinates) <= 2:
        return coordinates.copy()

    # 将坐标转换为numpy数组便于计算
    points = np.array(coordinates)

    # Douglas-Peucker算法实现
    def douglas_peucker(points, tolerance):
        if len(points) <= 2:
            return points

        # 找到距离首尾连线最远的点
        dmax = 0
        index = 0
        line_vec = points[-1] - points[0]
        line_len = np.linalg.norm(line_vec)

        if line_len > 0:
            line_vec /= line_len
            for i in range(1, len(points) - 1):
                point_vec = points[i] - points[0]
                # 计算点到线的垂直距离
                d = np.linalg.norm(np.cross(point_vec, line_vec))
                if d > dmax:
                    dmax = d
                    index = i

        # 递归处理
        if dmax > tolerance:
            left = douglas_peucker(points[:index + 1], tolerance)
            right = douglas_peucker(points[index:], tolerance)
            return np.vstack((left[:-1], right))
        else:
            return np.vstack((points[0], points[-1]))

    # 高质量模式先使用径向距离简化
    if highest_quality:
        # 计算各点之间的径向距离
        distances = np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1))
        avg_distance = np.mean(distances)

        # 使用径向距离进行初步简化
        mask = np.zeros(len(points), dtype=bool)
        mask[0] = True
        mask[-1] = True
        cum_dist = 0

        for i in range(1, len(points) - 1):
            cum_dist += distances[i - 1]
            if cum_dist >= avg_distance:
                mask[i] = True
                cum_dist = 0

        points = points[mask]

    # 应用Douglas-Peucker算法
    simplified = douglas_peucker(points, tolerance)

    return [tuple(p) for p in simplified]


def smooth_coordinates(coordinates, smoothing_factor=0.5, num_points=None):
    """
    改进版的轨迹平滑函数，更好地保持原始形状特征

    参数:
        coordinates: 坐标列表 [(lat1, lon1), (lat2, lon2), ...]
        smoothing_factor: 平滑因子 (0-1之间，越小越接近原始轨迹)
        num_points: 输出的点数 (None则保持原数量)

    返回:
        平滑后的坐标列表
    """
    if len(coordinates) <= 2:
        return coordinates.copy()

    points = np.array(coordinates)

    # 改进的参数化方式 - 使用弦长参数化
    diff = np.diff(points, axis=0)
    dist = np.sqrt((diff ** 2).sum(axis=1))
    cumdist = np.r_[0, np.cumsum(dist)]
    total_dist = cumdist[-1]

    # 归一化参数，确保曲线闭合时参数也闭合
    if np.linalg.norm(points[0] - points[-1]) < 1e-6:  # 近似闭合曲线
        t = cumdist / total_dist
    else:
        t = np.linspace(0, 1, len(points))

    # 调整平滑因子基于轨迹复杂度
    complexity = total_dist / len(points)  # 平均段长度
    adjusted_smoothing = smoothing_factor * complexity * 0.1

    try:
        # 使用更合适的样条阶数
        k = min(3, len(points) - 1)
        tck, u = splprep(points.T, u=t, s=adjusted_smoothing, k=k, nest=-1)

        # 计算插值点
        if num_points is None:
            num_points = len(points)
        u_new = np.linspace(u[0], u[-1], num_points)
        smoothed = splev(u_new, tck)

        # 对于闭合曲线，确保首尾一致
        if np.linalg.norm(points[0] - points[-1]) < 1e-6:
            smoothed = [np.r_[arr, arr[0]] for arr in smoothed]

        smoothed_points = list(zip(smoothed[0], smoothed[1]))
        return smoothed_points
    except Exception as e:
        print(f"平滑失败，返回原始轨迹: {str(e)}")
        return coordinates


def create_enhanced_running_track_svg(coordinates, output_file='running_track.svg', width=800, height=600,
                                      line_color='blue', line_width=2, bg_color='white',
                                      simplify=True, simplify_tolerance=0.0001, highest_quality=False,
                                      smooth=True, smoothing_factor=0.5):
    """
    增强版跑步轨迹SVG生成器

    参数:
        coordinates: 包含经纬度坐标的列表，格式为[(lat1, lon1), (lat2, lon2), ...]
        output_file: 输出的SVG文件名
        width: SVG画布宽度
        height: SVG画布高度
        line_color: 轨迹线颜色
        line_width: 轨迹线宽度
        bg_color: 背景颜色
        simplify: 是否简化轨迹
        simplify_tolerance: 简化容忍度
        highest_quality: 是否使用高质量简化
        smooth: 是否平滑轨迹
        smoothing_factor: 平滑因子 (0-1之间)
    """
    if not coordinates:
        raise ValueError("坐标点列表不能为空")

    # 预处理坐标
    processed_coords = coordinates.copy()

    # 坐标简化
    if simplify and len(processed_coords) > 100:  # 只有点数较多时才简化
        processed_coords = simplify_coordinates(
            processed_coords,
            tolerance=simplify_tolerance,
            highest_quality=highest_quality
        )

    # 坐标平滑
    if smooth and len(processed_coords) > 2:
        processed_coords = smooth_coordinates(
            processed_coords,
            smoothing_factor=smoothing_factor
        )

    create_running_track_svg_with_path(processed_coords, output_file, width=width, height=height, line_color=line_color,
                                       line_width=line_width, bg_color=bg_color, )
    # # 计算坐标范围以进行归一化
    # lats = [coord[0] for coord in processed_coords]
    # lons = [coord[1] for coord in processed_coords]
    #
    # min_lat, max_lat = min(lats), max(lats)
    # min_lon, max_lon = min(lons), max(lons)
    #
    # # 创建SVG根元素
    # svg = ET.Element('svg', {
    #     'xmlns': 'http://www.w3.org/2000/svg',
    #     'width': str(width),
    #     'height': str(height),
    #     'viewBox': f'0 0 {width} {height}'
    # })
    #
    # # 添加背景矩形
    # bg_rect = ET.SubElement(svg, 'rect', {
    #     'width': '100%',
    #     'height': '100%',
    #     'fill': bg_color
    # })
    #
    # # 将GPS坐标转换为SVG坐标
    # svg_points = []
    # for lat, lon in processed_coords:
    #     # 归一化到0-1范围
    #     norm_x = (lon - min_lon) / (max_lon - min_lon) if max_lon != min_lon else 0.5
    #     norm_y = (lat - min_lat) / (max_lat - min_lat) if max_lat != min_lat else 0.5
    #
    #     # 转换为SVG坐标，考虑SVG的Y轴是向下的
    #     x = norm_x * (width - 20) + 10  # 加边距
    #     y = (1 - norm_y) * (height - 20) + 10  # 反转Y轴并加边距
    #     svg_points.append(f"{x:.2f},{y:.2f}")
    #
    # # 创建折线元素
    # polyline = ET.SubElement(svg, 'polyline', {
    #     'points': ' '.join(svg_points),
    #     'fill': 'none',
    #     'stroke': line_color,
    #     'stroke-width': str(line_width),
    #     'stroke-linejoin': 'round',
    #     'stroke-linecap': 'round'
    # })
    #
    # # 添加起点和终点标记
    # if False and len(svg_points) >= 2:
    #     start_point = svg_points[0].split(',')
    #     end_point = svg_points[-1].split(',')
    #
    #     # 起点圆形标记
    #     ET.SubElement(svg, 'circle', {
    #         'cx': start_point[0],
    #         'cy': start_point[1],
    #         'r': '5',
    #         'fill': 'green'
    #     })
    #
    #     # 终点圆形标记
    #     ET.SubElement(svg, 'circle', {
    #         'cx': end_point[0],
    #         'cy': end_point[1],
    #         'r': '5',
    #         'fill': 'red'
    #     })
    #
    # # 添加统计信息
    # # stats_text = f"原始点数: {len(coordinates)} | 处理后点数: {len(processed_coords)}"
    # # ET.SubElement(svg, 'text', {
    # #     'x': '10',
    # #     'y': '20',
    # #     'font-family': 'Arial',
    # #     'font-size': '12',
    # #     'fill': 'black'
    # # }).text = stats_text
    #
    # # 生成SVG字符串并美化输出
    # rough_string = ET.tostring(svg, 'utf-8')
    # reparsed = minidom.parseString(rough_string)
    # pretty_svg = reparsed.toprettyxml(indent="  ")
    #
    # # 写入文件
    # with open(output_file, 'w') as f:
    #     f.write(pretty_svg)


def create_running_track_svg_with_path(coordinates, output_file='running_track.svg', width=800, height=600,
                                       line_color='blue', line_width=2, bg_color='white'):
    """
    使用SVG Path元素绘制跑步轨迹

    参数:
        coordinates: 包含经纬度坐标的列表，格式为[(lat1, lon1), (lat2, lon2), ...]
        output_file: 输出的SVG文件名
        width: SVG画布宽度
        height: SVG画布高度
        line_color: 轨迹线颜色
        line_width: 轨迹线宽度
        bg_color: 背景颜色
    """
    if not coordinates:
        raise ValueError("坐标点列表不能为空")

    # 计算坐标范围以进行归一化
    lats = [coord[0] for coord in coordinates]
    lons = [coord[1] for coord in coordinates]

    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    # 创建SVG根元素
    svg = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'width': str(width),
        'height': str(height),
        'viewBox': f'0 0 {width} {height}'
    })

    # 添加背景矩形
    # bg_rect = ET.SubElement(svg, 'rect', {
    #     'width': '100%',
    #     'height': '100%',
    #     'fill': bg_color
    # })

    # 将GPS坐标转换为SVG坐标并生成Path数据
    path_data = []
    for i, (lat, lon) in enumerate(coordinates):
        # 归一化到0-1范围
        norm_x = (lon - min_lon) / (max_lon - min_lon) if max_lon != min_lon else 0.5
        norm_y = (lat - min_lat) / (max_lat - min_lat) if max_lat != min_lat else 0.5

        # 转换为SVG坐标，考虑SVG的Y轴是向下的
        x = norm_x * (width - 20) + 10  # 加边距
        y = (1 - norm_y) * (height - 20) + 10  # 反转Y轴并加边距

        if i == 0:
            path_data.append(f"M {x:.2f} {y:.2f}")
        else:
            path_data.append(f"L {x:.2f} {y:.2f}")

    # 创建Path元素
    path = ET.SubElement(svg, 'path', {
        'd': ' '.join(path_data),
        'fill': 'none',
        'stroke': line_color,
        'stroke-width': str(line_width),
        'stroke-linejoin': 'round',
        'stroke-linecap': 'round'
    })

    # 添加起点和终点标记
    # if len(coordinates) >= 2:
    #     # 获取起点坐标
    #     first = coordinates[0]
    #     norm_x = (first[1] - min_lon) / (max_lon - min_lon) if max_lon != min_lon else 0.5
    #     norm_y = (first[0] - min_lat) / (max_lat - min_lat) if max_lat != min_lat else 0.5
    #     start_x = norm_x * (width - 20) + 10
    #     start_y = (1 - norm_y) * (height - 20) + 10
    #
    #     # 获取终点坐标
    #     last = coordinates[-1]
    #     norm_x = (last[1] - min_lon) / (max_lon - min_lon) if max_lon != min_lon else 0.5
    #     norm_y = (last[0] - min_lat) / (max_lat - min_lat) if max_lat != min_lat else 0.5
    #     end_x = norm_x * (width - 20) + 10
    #     end_y = (1 - norm_y) * (height - 20) + 10
    #
    #     # 起点圆形标记
    #     ET.SubElement(svg, 'circle', {
    #         'cx': f"{start_x:.2f}",
    #         'cy': f"{start_y:.2f}",
    #         'r': '5',
    #         'fill': 'green'
    #     })
    #
    #     # 终点圆形标记
    #     ET.SubElement(svg, 'circle', {
    #         'cx': f"{end_x:.2f}",
    #         'cy': f"{end_y:.2f}",
    #         'r': '5',
    #         'fill': 'red'
    #     })

    # 生成SVG字符串并美化输出
    rough_string = ET.tostring(svg, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_svg = reparsed.toprettyxml(indent="  ")

    # 写入文件
    with open(output_file, 'w') as f:
        f.write(pretty_svg)


# 示例使用
if __name__ == '__main__':
    # 生成模拟GPS轨迹数据（螺旋形轨迹）
    def generate_spiral_track(center_lat, center_lon, radius=0.01, points=500):
        coords = []
        for i in range(points):
            angle = 2 * math.pi * i / (points / 5)  # 绕5圈
            r = radius * i / points
            lat = center_lat + r * math.sin(angle)
            lon = center_lon + r * math.cos(angle)
            # 添加一些随机噪声模拟GPS误差
            lat += (random.random() - 0.5) * radius * 0.05
            lon += (random.random() - 0.5) * radius * 0.05
            coords.append((lat, lon))
        return coords


    import random

    random.seed(42)

    # 生成模拟轨迹数据
    # sample_coords = generate_spiral_track(40.7128, -74.0060, points=1000)
    sample_coords = parse_tcx_coordinates("/Users/liyutao/Downloads/13238395397.tcx")

    # 生成SVG - 原始轨迹
    create_enhanced_running_track_svg(
        sample_coords,
        'running_track_original.svg',
        width=256,
        height=256,
        simplify=False,
        smooth=False
    )

    # 生成SVG - 简化后的轨迹
    create_enhanced_running_track_svg(
        sample_coords,
        'running_track_simplified.svg',
        width=256,
        height=256,
        simplify=True,
        simplify_tolerance=0.0002,
        highest_quality=True,
        smooth=False
    )

    # 生成SVG - 平滑后的轨迹
    create_enhanced_running_track_svg(
        sample_coords,
        'running_track_smoothed.svg',
        width=256,
        height=256,
        simplify=False,
        smooth=True,
        smoothing_factor=0.01
    )

    # 生成SVG - 简化并平滑的轨迹
    create_enhanced_running_track_svg(
        sample_coords,
        'running_track_enhanced.svg',
        width=256,
        height=256,
        simplify=True,
        simplify_tolerance=0.0002,
        highest_quality=True,
        smooth=True,
        smoothing_factor=0.01
    )
