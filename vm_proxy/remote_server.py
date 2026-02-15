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
