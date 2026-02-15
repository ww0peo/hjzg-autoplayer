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
