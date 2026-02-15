"""
远程屏幕检测器 - 主机端使用

继承原有的 ScreenDetector，但截图从远程虚拟机获取
"""

from screen_detector import ScreenDetector
from remote_client import SyncRemoteGameClient
import cv2
import numpy as np


class RemoteScreenDetector(ScreenDetector):
    """
    远程屏幕检测器

    通过网络连接虚拟机，获取截图并使用 YOLO 模型检测
    """

    def __init__(self, vm_host: str, vm_port: int = 8765,
                 model_path: str = "hjzgv1.pt", conf: float = 0.25):
        """
        初始化远程检测器

        Args:
            vm_host: 虚拟机 IP 地址或主机名
            vm_port: 虚拟机代理服务端口
            model_path: YOLO 模型路径
            conf: 置信度阈值
        """
        # 初始化父类（但不加载模型，因为父类的构造函数会尝试本地截图）
        # 我们手动加载模型
        from ultralytics import YOLO

        # 禁用 SSL 验证
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context

        import urllib3
        import os
        import sys

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['REQUESTS_CA_BUNDLE'] = ''

        # 获取模型路径
        def get_resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

        model_path = get_resource_path(model_path)

        # 加载 YOLO 模型
        self.model = YOLO(model_path)
        self.conf = conf
        self.class_names = self.model.names

        print(f"模型加载成功: {model_path}")
        print(f"支持的类别: {self.class_names}")

        # 连接到虚拟机
        self.remote_client = SyncRemoteGameClient(vm_host, vm_port)
        print(f"正在连接虚拟机 {vm_host}:{vm_port} ...")
        self.remote_client.connect()
        print("虚拟机连接成功！")

    def capture_screen(self, region=None, quality: int = 85) -> np.ndarray:
        """
        截取远程虚拟机屏幕

        Args:
            region: 截取区域（暂不支持，全屏截图）
            quality: JPEG 质量

        Returns:
            numpy 数组格式的图像 (BGR)
        """
        if region:
            print("警告：远程检测器暂不支持区域截图，返回全屏")

        # 从虚拟机获取截图
        frame = self.remote_client.capture_screen(quality=quality)

        return frame

    def __del__(self):
        """析构时断开连接"""
        if hasattr(self, 'remote_client'):
            self.remote_client.disconnect()
