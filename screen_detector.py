from ultralytics import YOLO
import numpy as np
from PIL import ImageGrab
import cv2
from typing import Optional, Tuple, List, Dict
import os
import sys
import urllib3

# 禁用 SSL 警告和验证
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，支持打包后的环境"""
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ScreenDetector:
    """
    屏幕目标检测类

    功能：
    1. 加载YOLO模型
    2. 实时检测屏幕中的目标
    3. 获取指定对象的中心点位置
    """

    def __init__(self, model_path: str = "hjzgv1.pt", conf: float = 0.25):
        """
        初始化检测器

        参数:
            model_path: YOLO模型路径
            conf: 置信度阈值
        """
        # 禁用 SSL 验证
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context

        # 获取模型文件的正确路径（支持打包后的环境）
        model_path = get_resource_path(model_path)

        self.model = YOLO(model_path)
        self.conf = conf
        self.class_names = self.model.names  # 获取类别名称
        print(f"模型加载成功: {model_path}")
        print(f"支持的类别: {self.class_names}")

    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        截取屏幕

        参数:
            region: 截取区域 (x1, y1, x2, y2)，None表示全屏

        返回:
            numpy数组格式的图像 (BGR)
        """
        if region:
            screenshot = ImageGrab.grab(bbox=region)
        else:
            screenshot = ImageGrab.grab()

        # 转换为numpy数组并从RGB转为BGR
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame

    def detect_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> List[Dict]:
        """
        检测屏幕中的目标

        参数:
            region: 检测区域 (x1, y1, x2, y2)，None表示全屏

        返回:
            检测结果列表，每个元素包含:
            {
                'name': 类别名称,
                'confidence': 置信度,
                'bbox': [x1, y1, x2, y2],
                'center': (center_x, center_y)
            }
        """
        # 截取屏幕
        frame = self.capture_screen(region)

        # YOLO检测
        results = self.model.predict(source=frame, conf=self.conf, verbose=False)

        # 解析结果
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # 获取边界框坐标
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                # 计算中心点
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                # 获取类别和置信度
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                name = self.class_names[cls_id]

                detections.append({
                    'name': name,
                    'confidence': conf,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'center': (center_x, center_y)
                })

        return detections

    def get_center_by_name(self, name: str, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int]]:
        """
        获取指定名称对象的中心点位置

        参数:
            name: 目标类别名称（如 'person', 'boss', 'props'）
            region: 检测区域 (x1, y1, x2, y2)，None表示全屏

        返回:
            (center_x, center_y) 或 None（未检测到）
        """
        detections = self.detect_screen(region)

        # 查找匹配的目标
        for det in detections:
            if det['name'] == name:
                return det['center']

        return None

    def get_all_centers_by_name(self, name: str, region: Optional[Tuple[int, int, int, int]] = None) -> List[Tuple[int, int]]:
        """
        获取所有指定名称对象的中心点位置（可能有多个）

        参数:
            name: 目标类别名称
            region: 检测区域

        返回:
            中心点列表 [(x1, y1), (x2, y2), ...]
        """
        detections = self.detect_screen(region)

        centers = []
        for det in detections:
            if det['name'] == name:
                centers.append(det['center'])

        return centers

    def get_closest_center_by_name(self, name: str, reference_point: Tuple[int, int],
                                   region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int]]:
        """
        获取距离参考点最近的指定对象中心点

        参数:
            name: 目标类别名称
            reference_point: 参考点坐标 (x, y)
            region: 检测区域

        返回:
            最近的中心点 (x, y) 或 None
        """
        centers = self.get_all_centers_by_name(name, region)

        if not centers:
            return None

        # 计算距离并找到最近的点
        ref_x, ref_y = reference_point
        min_distance = float('inf')
        closest_center = None

        for center in centers:
            cx, cy = center
            distance = np.sqrt((cx - ref_x)**2 + (cy - ref_y)**2)
            if distance < min_distance:
                min_distance = distance
                closest_center = center

        return closest_center

    def get_all_detections(self, region: Optional[Tuple[int, int, int, int]] = None) -> Dict[str, List[Tuple[int, int]]]:
        """
        获取所有检测到的对象，按类别分组

        参数:
            region: 检测区域

        返回:
            字典 {'类别名': [(x1, y1), (x2, y2), ...]}
        """
        detections = self.detect_screen(region)

        result = {}
        for det in detections:
            name = det['name']
            center = det['center']

            if name not in result:
                result[name] = []
            result[name].append(center)

        return result

    def visualize_detections(self, region: Optional[Tuple[int, int, int, int]] = None,
                            show_time: int = 0) -> np.ndarray:
        """
        可视化检测结果

        参数:
            region: 检测区域
            show_time: 显示时间（毫秒），0表示按任意键继续

        返回:
            标注后的图像
        """
        frame = self.capture_screen(region)
        detections = self.detect_screen(region)

        # 绘制检测框和中心点
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            center_x, center_y = det['center']
            name = det['name']
            conf = det['confidence']

            # 绘制边界框
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # 绘制中心点
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

            # 绘制标签
            label = f"{name} {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # 绘制中心点坐标
            coord_text = f"({center_x}, {center_y})"
            cv2.putText(frame, coord_text, (center_x + 10, center_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        # 显示图像
        cv2.imshow('Screen Detection', frame)
        cv2.waitKey(show_time)

        return frame


# 使用示例
if __name__ == "__main__":
    # 创建检测器
    detector = ScreenDetector(model_path="hjzgv1.pt", conf=0.25)

    # # 示例1: 获取指定对象的中心点
    # print("\n=== 示例1: 获取boss的中心点 ===")
    # boss_center = detector.get_center_by_name('boss')
    # if boss_center:
    #     print(f"Boss中心点: {boss_center}")
    # else:
    #     print("未检测到Boss")

    # # 示例2: 获取所有person的中心点
    # print("\n=== 示例2: 获取所有person的中心点 ===")
    # person_centers = detector.get_all_centers_by_name('person')
    # print(f"检测到 {len(person_centers)} 个person")
    # for i, center in enumerate(person_centers):
    #     print(f"Person {i+1}: {center}")

    # # 示例3: 获取距离屏幕中心最近的props
    # print("\n=== 示例3: 获取距离屏幕中心最近的props ===")
    # screen_center = (960, 540)  # 假设1920x1080分辨率
    # closest_props = detector.get_closest_center_by_name('props', screen_center)
    # if closest_props:
    #     print(f"最近的Props中心点: {closest_props}")
    # else:
    #     print("未检测到Props")

    # # 示例4: 获取所有检测结果
    # print("\n=== 示例4: 获取所有检测结果 ===")
    # all_detections = detector.get_all_detections()
    # for name, centers in all_detections.items():
    #     print(f"{name}: {len(centers)} 个目标")
    #     for center in centers:
    #         print(f"  - {center}")

    # # 示例5: 可视化检测结果
    # print("\n=== 示例5: 可视化检测结果 ===")
    # print("按任意键关闭窗口...")
    # detector.visualize_detections(show_time=0)
    # cv2.destroyAllWindows()

    # # 示例6: 指定区域检测
    # print("\n=== 示例6: 检测屏幕左上角区域 ===")
    # region = (0, 0, 800, 600)  # 左上角800x600区域
    # boss_in_region = detector.get_center_by_name('boss', region=region)
    # print(f"区域内Boss中心点: {boss_in_region}")

    while True:
        # 实时检测屏幕
        detections = detector.detect_screen()
        print(f"实时检测到 {len(detections)} 个目标")
        for det in detections:
            print(f"{det['name']} at {det['center']} with confidence {det['confidence']:.2f}")

        # 每5秒检测一次
        cv2.waitKey(1000)

        # 按q退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
