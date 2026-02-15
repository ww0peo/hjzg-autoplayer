"""
远程游戏客户端 - 主机端使用

连接到虚拟机的代理服务器，提供截图和输入接口
"""

import websockets
import json
import asyncio
import base64
import numpy as np
import cv2
import time
from typing import Optional, Tuple, List


class RemoteGameClient:
    """远程游戏客户端"""

    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        初始化客户端

        Args:
            host: 虚拟机IP地址或主机名
            port: 端口号
        """
        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False
        self.timeout = 5.0

    async def connect(self):
        """连接到虚拟机代理服务器"""
        try:
            print(f"连接到 {self.uri} ...")
            self.websocket = await asyncio.wait_for(
                websockets.connect(self.uri),
                timeout=self.timeout
            )
            self.is_connected = True
            print("连接成功！")
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """断开连接"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            print("已断开连接")

    async def capture_screen(self, quality: int = 85) -> np.ndarray:
        """
        截取虚拟机屏幕

        Args:
            quality: JPEG 质量 (1-100)

        Returns:
            numpy 数组格式的图像 (BGR)
        """
        if not self.is_connected:
            raise ConnectionError("未连接到虚拟机")

        # 发送截图请求
        await self.send_message({
            "command": "capture",
            "quality": quality
        })

        # 接收响应
        response = await self.receive_message()

        if response.get("type") == "screenshot":
            # 解码 base64 图像
            img_data = base64.b64decode(response.get("data", ""))
            img_array = np.frombuffer(img_data, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img
        else:
            raise Exception(f"截图失败: {response}")

    async def click(self, x: int, y: int, button: str = 'left', click_type: str = 'single'):
        """
        在虚拟机上点击

        Args:
            x, y: 坐标
            button: 'left' 或 'right'
            click_type: 'single' 或 'double'
        """
        if not self.is_connected:
            raise ConnectionError("未连接到虚拟机")

        await self.send_message({
            "command": "click",
            "x": x,
            "y": y,
            "button": button,
            "click_type": click_type
        })

        response = await self.receive_message()
        return response.get("data", {})

    async def move_mouse(self, x: int, y: int):
        """移动鼠标到指定位置"""
        if not self.is_connected:
            raise ConnectionError("未连接到虚拟机")

        await self.send_message({
            "command": "move",
            "x": x,
            "y": y
        })

        response = await self.receive_message()
        return response.get("data", {})

    async def press_key(self, key: str, duration: float = 0.05):
        """
        按键

        Args:
            key: 键名（如 'a', 'space', 'enter'）
            duration: 按键持续时间
        """
        if not self.is_connected:
            raise ConnectionError("未连接到虚拟机")

        await self.send_message({
            "command": "key",
            "key": key,
            "duration": duration
        })

        response = await self.receive_message()
        return response.get("data", {})

    async def ping(self):
        """心跳检测"""
        if not self.is_connected:
            return False

        await self.send_message({"command": "ping"})
        response = await self.receive_message()
        return response.get("type") == "pong"

    async def send_message(self, data: dict):
        """发送消息到服务器"""
        try:
            await self.websocket.send(json.dumps(data))
        except Exception as e:
            print(f"发送消息失败: {e}")
            self.is_connected = False
            raise

    async def receive_message(self) -> dict:
        """接收服务器消息"""
        try:
            message = await asyncio.wait_for(
                self.websocket.recv(),
                timeout=self.timeout
            )
            return json.loads(message)
        except Exception as e:
            print(f"接收消息失败: {e}")
            self.is_connected = False
            raise

    async def get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸（默认 1920x1080）"""
        # TODO: 可以从服务器获取真实尺寸
        return (1920, 1080)


# 同步包装器（为了兼容现有代码）
class SyncRemoteGameClient:
    """同步版本的远程客户端（兼容现有代码）"""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.async_client = RemoteGameClient(host, port)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def connect(self):
        """同步连接"""
        return self.loop.run_until_complete(self.async_client.connect())

    def disconnect(self):
        """同步断开"""
        return self.loop.run_until_complete(self.async_client.disconnect())

    def capture_screen(self, quality: int = 85) -> np.ndarray:
        """同步截图"""
        return self.loop.run_until_complete(self.async_client.capture_screen(quality))

    def click(self, x: int, y: int, button: str = 'left', click_type: str = 'single'):
        """同步点击"""
        return self.loop.run_until_complete(
            self.async_client.click(x, y, button, click_type)
        )

    def move_mouse(self, x: int, y: int):
        """同步移动鼠标"""
        return self.loop.run_until_complete(self.async_client.move_mouse(x, y))

    def press_key(self, key: str, duration: float = 0.05):
        """同步按键"""
        return self.loop.run_until_complete(self.async_client.press_key(key, duration))

    def get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸"""
        return self.loop.run_until_complete(self.async_client.get_screen_size())

    def __del__(self):
        """析构时关闭事件循环"""
        self.loop.close()


# 使用示例
if __name__ == "__main__":
    async def test_client():
        client = RemoteGameClient("192.168.1.100", 8765)

        # 连接
        if await client.connect():
            # 测试截图
            print("正在截图...")
            img = await client.capture_screen(quality=85)
            print(f"截图成功，尺寸: {img.shape}")

            # 保存截图
            cv2.imwrite("test_screenshot.png", img)
            print("截图已保存为 test_screenshot.png")

            # 测试点击
            print("测试点击屏幕中心...")
            screen_w, screen_h = await client.get_screen_size()
            await client.click(screen_w // 2, screen_h // 2)
            print("点击完成")

            # 测试按键
            print("测试按键...")
            await client.press_key('space')
            print("按键完成")

            # 断开连接
            await client.disconnect()
        else:
            print("连接失败")

    # 运行测试
    asyncio.run(test_client())
