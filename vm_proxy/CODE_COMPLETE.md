# 虚拟机自动化方案 - 完整代码清单

## ✅ 验证结果

**原有代码状态：** ✅ **完全未修改**
- 所有原有文件保持不变
- Git 状态显示没有修改文件
- 仅新增 `vm_proxy/` 目录

**模块隔离：** ✅ **完全独立**
- 虚拟机远程功能完全独立于原有代码
- 不影响原有的本地自动化功能
- 两套代码可以共存使用

---

## 📦 文件清单

### 核心代码（5个 Python 文件）

| 文件 | 行数 | 说明 | 位置 |
|------|------|------|------|
| `remote_server.py` | 180 | 虚拟机代理服务器 | 虚拟机 |
| `remote_client.py` | 230 | 主机网络客户端 | 主机 |
| `remote_screen_detector.py` | 85 | 远程屏幕检测器 | 主机 |
| `remote_game_input.py` | 100 | 远程游戏输入 | 主机 |
| `remote_gui_script.py` | 490 | 主机GUI控制台 | 主机 |

### 启动脚本（2个批处理文件）

| 文件 | 说明 | 位置 |
|------|------|------|
| `start_vm_server.bat` | 虚拟机启动脚本 | 虚拟机 |
| `start_host_client.bat` | 主机启动脚本 | 主机 |

### 配置和文档（4个文件）

| 文件 | 说明 | 用途 |
|------|------|------|
| `config.json` | 配置文件 | IP、端口配置 |
| `README.md` | 详细文档 | 技术参考 |
| `SETUP_GUIDE.md` | 快速指南 | 5步部署 |
| `PROJECT_STRUCTURE.md` | 架构文档 | 数据流图 |

---

## 🔧 代码完整性验证

### 原有代码（未修改）
```
✅ gui_script.py              - 完整保留
✅ screen_detector.py          - 完整保留
✅ game_input_advanced.py      - 完整保留
✅ game_utils.py               - 完整保留
✅ scripts/                    - 完整保留
✅ hjzgv1.pt                   - 完整保留
✅ 启动GUI.bat                 - 完整保留
```

### 新增代码（独立模块）
```
🆕 vm_proxy/__init__.py              - 模块初始化
🆕 vm_proxy/remote_server.py         - 虚拟机服务器
🆕 vm_proxy/remote_client.py         - 主机客户端
🆕 vm_proxy/remote_screen_detector.py - 远程检测
🆕 vm_proxy/remote_game_input.py     - 远程输入
🆕 vm_proxy/remote_gui_script.py     - 远程GUI
🆕 vm_proxy/start_vm_server.bat      - 虚拟机启动
🆕 vm_proxy/start_host_client.bat    - 主机启动
🆕 vm_proxy/config.json              - 配置文件
🆕 vm_proxy/README.md                - 详细文档
🆕 vm_proxy/SETUP_GUIDE.md           - 快速指南
🆕 vm_proxy/PROJECT_STRUCTURE.md     - 架构文档
```

---

## 📋 完整代码文件列表

### 1. vm_proxy/__init__.py
```python
"""
虚拟机远程自动化模块

本模块提供虚拟机游戏自动化功能，允许在主机上控制虚拟机中的游戏。
所有原有代码保持不变，本模块作为独立增强功能存在。

模块结构：
- remote_server.py: 虚拟机端代理服务器
- remote_client.py: 主机端网络客户端
- remote_screen_detector.py: 远程屏幕检测器
- remote_game_input.py: 远程游戏输入
- remote_gui_script.py: 主机端GUI控制台
"""

__version__ = "1.0.0"
__author__ = "OpenClaw"
```

### 2. vm_proxy/remote_server.py
**位置：** 虚拟机
**大小：** 180 行
**依赖：** websockets, numpy, opencv-python, pillow, pyautogui

```python
"""
虚拟机游戏代理服务器

提供网络接口给主机控制虚拟机内的游戏
功能：
1. 截图服务：返回游戏画面的截图（base64 或 URL）
2. 输入服务：接收主机发送的鼠标/键盘指令
3. 双向通信：WebSocket 实时传输
"""

import asyncio
import websockets
import json
import base64
import cv2
import numpy as np
from PIL import ImageGrab
import pyautogui
import time
from typing import Dict, Any

# 配置
HOST = "0.0.0.0"  # 监听所有网络接口
PORT = 8765

# 设置 PyAutoGUI
pyautogui.PAUSE = 0.05
pyautogui.FAILSAFE = True


class GameProxyServer:
    """游戏代理服务器"""

    def __init__(self):
        self.clients = set()
        self.is_running = True

    async def capture_screen(self, quality: int = 85) -> str:
        """
        截取屏幕并返回 base64 编码

        Args:
            quality: JPEG 质量 (1-100)

        Returns:
            base64 编码的图像字符串
        """
        try:
            # 截取屏幕
            screenshot = ImageGrab.grab()

            # 转换为 numpy 数组
            img_array = np.array(screenshot)

            # 压缩为 JPEG 格式
            _, buffer = cv2.imencode('.jpg', img_array, [int(cv2.IMWRITE_JPEG_QUALITY), quality])

            # 转换为 base64
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            return img_base64
        except Exception as e:
            print(f"截图错误: {e}")
            return ""

    async def handle_mouse_click(self, x: int, y: int, button: str = 'left', click_type: str = 'single'):
        """处理鼠标点击"""
        try:
            pyautogui.moveTo(x, y, duration=0.1)

            if click_type == 'double':
                pyautogui.doubleClick(button=button)
            elif click_type == 'right':
                pyautogui.click(button='right')
            else:
                pyautogui.click(button=button)

            return {"success": True, "action": f"click {button} at ({x}, {y})"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def handle_key_press(self, key: str, duration: float = 0.05):
        """处理按键"""
        try:
            pyautogui.press(key, duration=duration)
            return {"success": True, "action": f"press key {key}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def handle_message(self, websocket, path):
        """处理客户端消息"""
        print(f"客户端已连接: {websocket.remote_address}")
        self.clients.add(websocket)

        try:
            async for message in websocket:
                data = json.loads(message)
                command = data.get('command')

                # 命令分发
                if command == 'capture':
                    # 截图请求
                    quality = data.get('quality', 85)
                    img_base64 = await self.capture_screen(quality)
                    response = {
                        "type": "screenshot",
                        "data": img_base64,
                        "timestamp": int(time.time() * 1000)
                    }
                    await websocket.send(json.dumps(response))

                elif command == 'click':
                    # 鼠标点击
                    x = data.get('x')
                    y = data.get('y')
                    button = data.get('button', 'left')
                    click_type = data.get('click_type', 'single')
                    result = await self.handle_mouse_click(x, y, button, click_type)
                    await websocket.send(json.dumps({"type": "response", "data": result}))

                elif command == 'key':
                    # 按键
                    key = data.get('key')
                    duration = data.get('duration', 0.05)
                    result = await self.handle_key_press(key, duration)
                    await websocket.send(json.dumps({"type": "response", "data": result}))

                elif command == 'move':
                    # 移动鼠标
                    x = data.get('x')
                    y = data.get('y')
                    pyautogui.moveTo(x, y, duration=0.1)
                    await websocket.send(json.dumps({"type": "response", "data": {"success": True}}))

                elif command == 'ping':
                    # 心跳检测
                    await websocket.send(json.dumps({"type": "pong"}))

                else:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"未知命令: {command}"
                    }))

        except websockets.exceptions.ConnectionClosed:
            print("客户端已断开")
        except Exception as e:
            print(f"处理消息错误: {e}")
        finally:
            self.clients.remove(websocket)

    async def broadcast(self, message: str):
        """向所有客户端广播消息"""
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )

    async def start(self):
        """启动服务器"""
        print(f"游戏代理服务器启动中...")
        print(f"监听地址: {HOST}:{PORT}")
        print(f"按 Ctrl+C 停止服务器")

        async with websockets.serve(self.handle_message, HOST, PORT):
            await asyncio.Future()  # 永久运行


async def main():
    """主函数"""
    server = GameProxyServer()
    await server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务器已停止")
```

### 3. vm_proxy/remote_client.py
**位置：** 主机
**大小：** 230 行
**依赖：** websockets, numpy, opencv-python

```python
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
```

### 4. vm_proxy/remote_screen_detector.py
**位置：** 主机
**大小：** 85 行
**依赖：** 继承 screen_detector.py

```python
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
```

### 5. vm_proxy/remote_game_input.py
**位置：** 主机
**大小：** 100 行
**依赖：** remote_client.py

```python
"""
远程游戏输入 - 主机端使用

替代原有的 WindowsInput，通过网络控制虚拟机
"""

from remote_client import SyncRemoteGameClient


class RemoteGameInput:
    """
    远程游戏输入控制器

    通过网络向虚拟机发送鼠标和键盘指令
    """

    def __init__(self, vm_host: str, vm_port: int = 8765):
        """
        初始化远程输入控制器

        Args:
            vm_host: 虚拟机 IP 地址或主机名
            vm_port: 虚拟机代理服务端口
        """
        self.remote_client = SyncRemoteGameClient(vm_host, vm_port)

        # 连接到虚拟机
        print(f"正在连接虚拟机 {vm_host}:{vm_port} ...")
        self.remote_client.connect()
        print("虚拟机连接成功！")

    def get_screen_size(self):
        """获取屏幕尺寸"""
        return self.remote_client.get_screen_size()

    def move_mouse(self, x, y):
        """移动鼠标到绝对坐标"""
        self.remote_client.move_mouse(x, y)

    def click(self, x=None, y=None, button='left', delay=0.05):
        """
        点击鼠标

        Args:
            x, y: 坐标（None则在当前位置点击）
            button: 'left' 或 'right'
            delay: 延迟（远程控制时此参数被忽略）
        """
        if x is not None and y is not None:
            self.move_mouse(x, y)

        # 发送点击指令
        click_type = 'double' if button == 'double' else 'single'
        self.remote_client.click(x or 0, y or 0, button=button, click_type=click_type)

    def double_click(self, x=None, y=None, delay=0.05):
        """双击"""
        if x is not None and y is not None:
            self.move_mouse(x, y)
        self.remote_client.click(x or 0, y or 0, click_type='double')

    def press_key(self, vk_code, delay=0.05):
        """
        按键

        Args:
            vk_code: 键名（如 'a', 'space', 'enter'）
            delay: 延迟（远程控制时此参数被忽略）

        注意：远程版本使用键名而不是虚拟键码
        """
        # 将虚拟键码转换为键名（简单映射）
        key_mapping = {
            0x20: 'space',
            0x0D: 'enter',
            0x1B: 'esc',
            0x09: 'tab',
        }

        # 如果是 ASCII 字符，直接使用
        if isinstance(vk_code, int) and vk_code >= ord('A') and vk_code <= ord('Z'):
            key = chr(vk_code).lower()
        elif isinstance(vk_code, int) and vk_code >= ord('0') and vk_code <= ord('9'):
            key = chr(vk_code)
        elif isinstance(vk_code, int):
            key = key_mapping.get(vk_code, 'space')
        else:
            key = str(vk_code)

        self.remote_client.press_key(key)

    def __del__(self):
        """析构时断开连接"""
        if hasattr(self, 'remote_client'):
            self.remote_client.disconnect()


# 兼容原有代码的别名
WindowsInput = RemoteGameInput  # 保持与原有代码的兼容性
```

### 6. vm_proxy/remote_gui_script.py
**位置：** 主机
**大小：** 490 行
**依赖：** Tkinter, 远程模块

```python
"""
远程游戏自动化脚本 - GUI版本（虚拟机架构）

修改自原版 gui_script.py，使用远程客户端替代本地输入/截图
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import time
from datetime import datetime
import json
import os

# 导入远程模块
from remote_screen_detector import RemoteScreenDetector
from remote_game_input import RemoteGameInput
from scripts.base_script import BaseScript


class RemoteGameAutomationGUI:
    """远程游戏自动化图形界面"""

    def __init__(self, root):
        self.root = root
        self.root.title("远程游戏自动化控制台")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # 状态变量
        self.is_running = False
        self.is_paused = False
        self.script_thread = None
        self.detector = None
        self.game_input = None
        self.current_script = None
        self.run_count = 0

        # 配置变量
        self.vm_host = tk.StringVar(value="192.168.1.100")
        self.vm_port = tk.IntVar(value=8765)
        self.window_title = tk.StringVar(value="Torchlight: Infinite")
        self.model_path = tk.StringVar(value="hjzgv1.pt")
        self.conf_threshold = tk.DoubleVar(value=0.5)

        # 获取所有可用脚本
        available_scripts = BaseScript.get_all_scripts()
        self.selected_script = tk.StringVar(
            value=list(available_scripts.keys())[0] if available_scripts else ""
        )

        # 连接状态
        self.is_connected = False

        # 创建界面
        self.create_widgets()

        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """创建界面组件"""

        # ===== 顶部配置区 =====
        config_frame = ttk.LabelFrame(self.root, text="配置", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        # 虚拟机配置
        ttk.Label(config_frame, text="虚拟机IP:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.vm_host, width=20).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(config_frame, text="端口:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.vm_port, width=10).grid(row=0, column=3, padx=5, pady=2)

        # 连接按钮
        self.connect_btn = ttk.Button(
            config_frame,
            text="🔌 连接虚拟机",
            command=self.connect_to_vm,
            width=15
        )
        self.connect_btn.grid(row=0, column=4, padx=5, pady=2)

        # 游戏配置
        ttk.Label(config_frame, text="模型路径:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.model_path, width=30).grid(row=1, column=1, columnspan=2, padx=5, pady=2)

        # 置信度
        ttk.Label(config_frame, text="置信度阈值:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(config_frame, from_=0.1, to=1.0, variable=self.conf_threshold,
                  orient=tk.HORIZONTAL, length=200).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(config_frame, textvariable=self.conf_threshold).grid(row=2, column=2, padx=5, pady=2)

        # 脚本选择
        ttk.Label(config_frame, text="选择脚本:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        script_combo = ttk.Combobox(config_frame, textvariable=self.selected_script,
                                     values=list(BaseScript.get_all_scripts().keys()),
                                     state='readonly', width=28)
        script_combo.grid(row=3, column=1, columnspan=2, padx=5, pady=2)
        script_combo.bind('<<ComboboxSelected>>', self.on_script_changed)

        # ===== 连接状态指示器 =====
        status_frame = ttk.Frame(self.root, padding=5)
        status_frame.pack(fill=tk.X, padx=10)

        ttk.Label(status_frame, text="连接状态:").pack(side=tk.LEFT, padx=5)

        self.connect_status_label = ttk.Label(
            status_frame,
            text="● 未连接",
            foreground="gray",
            font=("Arial", 10, "bold")
        )
        self.connect_status_label.pack(side=tk.LEFT, padx=5)

        # ===== 控制按钮区 =====
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 启动按钮
        self.start_btn = ttk.Button(
            control_frame,
            text="▶ 启动",
            command=self.start_script,
            width=20,
            state=tk.DISABLED
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        # 暂停按钮
        self.pause_btn = ttk.Button(
            control_frame,
            text="⏸ 暂停",
            command=self.pause_script,
            width=20,
            state=tk.DISABLED
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        # 停止按钮
        self.stop_btn = ttk.Button(
            control_frame,
            text="⏹ 停止",
            command=self.stop_script,
            width=20,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # 测试连接按钮
        ttk.Button(
            control_frame,
            text="🧪 测试连接",
            command=self.test_connection,
            width=15
        ).pack(side=tk.LEFT, padx=5)

        # ===== 运行状态指示器 =====
        run_status_frame = ttk.Frame(self.root, padding=5)
        run_status_frame.pack(fill=tk.X, padx=10)

        ttk.Label(run_status_frame, text="运行状态:").pack(side=tk.LEFT, padx=5)

        self.run_status_label = ttk.Label(
            run_status_frame,
            text="● 未启动",
            foreground="gray",
            font=("Arial", 10, "bold")
        )
        self.run_status_label.pack(side=tk.LEFT, padx=5)

        # 运行次数
        self.run_count_label = ttk.Label(run_status_frame, text="运行次数: 0")
        self.run_count_label.pack(side=tk.RIGHT, padx=5)

        # ===== 日志显示区 =====
        log_frame = ttk.LabelFrame(self.root, text="运行日志", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            height=20,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 配置日志颜色标签
        self.log_text.tag_config("INFO", foreground="black")
        self.log_text.tag_config("SUCCESS", foreground="green")
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("DEBUG", foreground="blue")

        # ===== 底部提示 =====
        hint_frame = ttk.Frame(self.root, padding=5)
        hint_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(
            hint_frame,
            text="💡 使用步骤: 1) 输入虚拟机IP → 2) 点击'连接虚拟机' → 3) 选择脚本 → 4) 点击'启动'",
            foreground="gray",
            font=("Arial", 8)
        ).pack()

    def log(self, message, level="INFO"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_message, level)
        self.log_text.see(tk.END)

    def connect_to_vm(self):
        """连接到虚拟机"""
        vm_host = self.vm_host.get()
        vm_port = self.vm_port.get()

        self.log(f"正在连接虚拟机 {vm_host}:{vm_port}...", "INFO")

        try:
            # 初始化检测器和输入控制器
            self.detector = RemoteScreenDetector(
                vm_host=vm_host,
                vm_port=vm_port,
                model_path=self.model_path.get(),
                conf=self.conf_threshold.get()
            )

            self.game_input = RemoteGameInput(
                vm_host=vm_host,
                vm_port=vm_port
            )

            self.is_connected = True
            self.connect_status_label.config(text="● 已连接", foreground="green")
            self.connect_btn.config(text="🔌 断开连接")
            self.start_btn.config(state=tk.NORMAL)

            self.log("虚拟机连接成功！", "SUCCESS")
            self.log(f"模型: {self.model_path.get()}", "INFO")
            self.log(f"置信度阈值: {self.conf_threshold.get()}", "INFO")

        except Exception as e:
            self.is_connected = False
            self.connect_status_label.config(text="● 连接失败", foreground="red")
            self.start_btn.config(state=tk.DISABLED)
            self.log(f"连接失败: {e}", "ERROR")

    def disconnect_from_vm(self):
        """断开虚拟机连接"""
        try:
            if self.detector:
                self.detector.__del__()
            if self.game_input:
                self.game_input.__del__()
        except:
            pass

        self.is_connected = False
        self.connect_status_label.config(text="● 未连接", foreground="gray")
        self.connect_btn.config(text="🔌 连接虚拟机")
        self.start_btn.config(state=tk.DISABLED)

        self.log("已断开虚拟机连接", "INFO")

    def test_connection(self):
        """测试连接"""
        if not self.is_connected:
            self.log("请先连接虚拟机", "WARNING")
            return

        try:
            self.log("正在测试连接...", "INFO")

            # 测试截图
            img = self.detector.capture_screen(quality=85)
            self.log(f"截图测试成功，尺寸: {img.shape}", "SUCCESS")

            # 测试点击屏幕中心
            screen_w, screen_h = self.game_input.get_screen_size()
            self.log(f"点击屏幕中心 ({screen_w//2}, {screen_h//2})...", "INFO")
            self.game_input.click(screen_w // 2, screen_h // 2)
            self.log("点击测试成功", "SUCCESS")

            self.log("连接测试完成！", "SUCCESS")

        except Exception as e:
            self.log(f"连接测试失败: {e}", "ERROR")

    def on_script_changed(self, event=None):
        """脚本选择改变时的回调"""
        script_name = self.selected_script.get()
        available_scripts = BaseScript.get_all_scripts()
        if script_name in available_scripts:
            script_class = available_scripts[script_name]
            temp_instance = script_class(self)
            description = temp_instance.get_description()
            self.log(f"已选择脚本: {script_name} - {description}", "INFO")

    def update_run_status(self, text, color):
        """更新运行状态指示器"""
        self.run_status_label.config(text=f"● {text}", foreground=color)

    def start_script(self):
        """启动脚本"""
        if not self.is_connected:
            self.log("请先连接虚拟机", "WARNING")
            return

        if self.is_running:
            if self.is_paused:
                self.is_paused = False
                self.update_run_status("运行中", "green")
                self.pause_btn.config(text="⏸ 暂停")
                self.log("脚本已恢复", "SUCCESS")
            else:
                self.log("脚本已在运行中", "WARNING")
            return

        self.is_running = True
        self.is_paused = False

        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)

        self.update_run_status("运行中", "green")
        self.log("=" * 50, "INFO")
        self.log("脚本启动", "SUCCESS")
        self.log("=" * 50, "INFO")

        self.script_thread = threading.Thread(target=self.run_script, daemon=True)
        self.script_thread.start()

    def pause_script(self):
        """暂停/恢复脚本"""
        if not self.is_running:
            self.log("脚本未运行", "WARNING")
            return

        if self.is_paused:
            self.is_paused = False
            self.update_run_status("运行中", "green")
            self.pause_btn.config(text="⏸ 暂停")
            self.log("脚本已恢复", "SUCCESS")
        else:
            self.is_paused = True
            self.update_run_status("已暂停", "orange")
            self.pause_btn.config(text="▶ 恢复")
            self.log("脚本已暂停", "WARNING")

    def stop_script(self):
        """停止脚本"""
        if not self.is_running:
            self.log("脚本未运行", "WARNING")
            return

        self.is_running = False
        self.is_paused = False

        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="⏸ 暂停")
        self.stop_btn.config(state=tk.DISABLED)

        self.update_run_status("已停止", "red")
        self.log("=" * 50, "INFO")
        self.log("脚本已停止", "ERROR")
        self.log("=" * 50, "INFO")

    def sleep(self, seconds):
        """可中断的睡眠"""
        start_time = time.time()
        while time.time() - start_time < seconds:
            if not self.is_running:
                return False
            while self.is_paused:
                time.sleep(0.1)
                if not self.is_running:
                    return False
            time.sleep(0.1)
        return True

    def run_script(self):
        """运行主脚本逻辑"""
        try:
            # 初始化选定的脚本
            script_name = self.selected_script.get()
            available_scripts = BaseScript.get_all_scripts()
            if script_name not in available_scripts:
                self.log(f"未找到脚本: {script_name}", "ERROR")
                return

            script_class = available_scripts[script_name]
            self.current_script = script_class(self)
            self.log(f"已加载脚本: {script_name}", "SUCCESS")
            self.log(f"脚本描述: {self.current_script.get_description()}", "INFO")

            if not self.sleep(2):
                return

            # 主循环
            while self.is_running:
                self.run_count += 1
                self.run_count_label.config(text=f"运行次数: {self.run_count}")
                self.log(f"\n>>> 开始第 {self.run_count} 次运行 <<<", "SUCCESS")

                # 执行脚本
                if not self.current_script.execute():
                    break

                self.log(f"<<< 第 {self.run_count} 次运行完成 >>>\n", "SUCCESS")

                # 等待下一次循环
                if not self.sleep(2):
                    break

        except Exception as e:
            self.log(f"脚本执行出错: {e}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
        finally:
            self.is_running = False
            self.current_script = None
            self.root.after(0, self.stop_script)

    def on_closing(self):
        """关闭窗口时的处理"""
        if self.is_running:
            self.stop_script()
            time.sleep(0.5)

        # 断开连接
        if self.is_connected:
            self.disconnect_from_vm()

        self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = RemoteGameAutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
```

---

## 🚀 启动脚本

### 7. vm_proxy/start_vm_server.bat
```batch
@echo off
REM ========================================
REM 虚拟机端 - 启动游戏代理服务器
REM ========================================

echo 正在启动虚拟机游戏代理服务器...
echo.

REM 激活虚拟环境（如果使用）
REM call .venv\Scripts\activate.bat

REM 安装依赖
echo 检查依赖...
pip show websockets >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install websockets numpy opencv-python pillow pyautogui
)

REM 启动服务器
echo 启动服务器...
python remote_server.py

pause
```

### 8. vm_proxy/start_host_client.bat
```batch
@echo off
REM ========================================
REM 主机端 - 启动远程自动化GUI
REM ========================================

echo 正在启动主机远程自动化GUI...
echo.

REM 激活虚拟环境（如果使用）
REM call .venv\Scripts\activate.bat

REM 安装依赖
echo 检查依赖...
pip show websockets >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install websockets numpy opencv-python pillow
)

REM 启动远程GUI
python remote_gui_script.py

pause
```

---

## ⚙️ 配置文件

### 9. vm_proxy/config.json
```json
{
  "vm_host": "192.168.1.100",
  "vm_port": 8765,
  "model_path": "hjzgv1.pt",
  "conf_threshold": 0.5,
  "window_title": "Torchlight: Infinite"
}
```

---

## 📚 文档文件

详细文档文件已在之前创建，包括：
- `README.md` - 技术文档
- `SETUP_GUIDE.md` - 快速设置指南
- `PROJECT_STRUCTURE.md` - 架构文档

---

## ✅ 验证清单

- [x] 原有代码完全未修改
- [x] 新增代码完全独立
- [x] 模块隔离清晰
- [x] 依赖关系明确
- [x] 文档完整齐全
- [x] 启动脚本完善
- [x] 配置文件独立

---

## 🎯 使用方法

### 虚拟机端
```bash
cd hjzg-autoplayer/vm_proxy
start_vm_server.bat
```

### 主机端
```bash
cd hjzg-autoplayer/vm_proxy
start_host_client.bat
```

---

**代码已完整创建！所有原有代码保持不变，新增的虚拟机自动化功能作为独立模块存在。** 🦞
