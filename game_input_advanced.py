"""
游戏输入高级方案 - 绕过游戏保护

PyAutoGUI在很多游戏中会被检测并屏蔽，需要使用更底层的输入方法
"""

import time
import ctypes
from ctypes import wintypes
import win32api
import win32con
import win32gui


# ============================================
# 方案1: 使用Windows API直接发送消息
# ============================================

class WindowsInput:
    """使用Windows API发送输入（更难被检测）"""

    # 鼠标事件常量
    MOUSEEVENTF_MOVE = 0x0001
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010
    MOUSEEVENTF_ABSOLUTE = 0x8000

    # 键盘事件常量
    KEYEVENTF_KEYUP = 0x0002

    def __init__(self):
        self.user32 = ctypes.windll.user32

    def get_screen_size(self):
        """获取屏幕尺寸"""
        return self.user32.GetSystemMetrics(0), self.user32.GetSystemMetrics(1)

    def move_mouse(self, x, y):
        """移动鼠标到绝对坐标"""
        screen_width, screen_height = self.get_screen_size()

        # 转换为绝对坐标（0-65535）
        abs_x = int(x * 65535 / screen_width)
        abs_y = int(y * 65535 / screen_height)

        self.user32.mouse_event(
            self.MOUSEEVENTF_MOVE | self.MOUSEEVENTF_ABSOLUTE,
            abs_x, abs_y, 0, 0
        )

    def click(self, x=None, y=None, button='left', delay=0.05):
        """
        点击鼠标

        参数:
            x, y: 坐标（None则在当前位置点击）
            button: 'left' 或 'right'
            delay: 按下和释放之间的延迟
        """
        if x is not None and y is not None:
            self.move_mouse(x, y)
            time.sleep(0.05)

        if button == 'left':
            down_flag = self.MOUSEEVENTF_LEFTDOWN
            up_flag = self.MOUSEEVENTF_LEFTUP
        else:
            down_flag = self.MOUSEEVENTF_RIGHTDOWN
            up_flag = self.MOUSEEVENTF_RIGHTUP

        # 按下
        self.user32.mouse_event(down_flag, 0, 0, 0, 0)
        time.sleep(delay)

        # 释放
        self.user32.mouse_event(up_flag, 0, 0, 0, 0)

    def double_click(self, x=None, y=None, delay=0.05):
        """双击"""
        self.click(x, y, delay=delay)
        time.sleep(0.05)
        self.click(delay=delay)

    def press_key(self, vk_code, delay=0.05):
        """
        按键

        常用虚拟键码:
            VK_SPACE = 0x20
            VK_RETURN = 0x0D (Enter)
            VK_ESCAPE = 0x1B
            VK_TAB = 0x09
            VK_SHIFT = 0x10
            VK_CONTROL = 0x11
            VK_ALT = 0x12

            字母: ord('A') - ord('Z')
            数字: ord('0') - ord('9')
            F1-F12: 0x70 - 0x7B
        """
        # 按下
        self.user32.keybd_event(vk_code, 0, 0, 0)
        time.sleep(delay)

        # 释放
        self.user32.keybd_event(vk_code, 0, self.KEYEVENTF_KEYUP, 0)


# ============================================
# 方案2: 使用PostMessage发送消息到窗口
# ============================================

class WindowMessageInput:
    """直接向窗口发送消息（最难被检测）"""

    def __init__(self, window_title=None, hwnd=None):
        """
        初始化

        参数:
            window_title: 窗口标题
            hwnd: 窗口句柄（如果已知）
        """
        if hwnd:
            self.hwnd = hwnd
        elif window_title:
            self.hwnd = win32gui.FindWindow(None, window_title)
            if not self.hwnd:
                raise Exception(f"未找到窗口: {window_title}")
        else:
            raise Exception("必须提供window_title或hwnd")

    def click(self, x, y, button='left'):
        """
        向窗口发送点击消息

        参数:
            x, y: 窗口内的相对坐标
            button: 'left' 或 'right'
        """
        # 构造lParam（坐标）
        lParam = win32api.MAKELONG(x, y)

        if button == 'left':
            # 发送鼠标左键按下
            win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
            time.sleep(0.05)

            # 发送鼠标左键释放
            win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, lParam)
        else:
            # 发送鼠标右键按下
            win32api.PostMessage(self.hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
            time.sleep(0.05)

            # 发送鼠标右键释放
            win32api.PostMessage(self.hwnd, win32con.WM_RBUTTONUP, 0, lParam)

    def double_click(self, x, y):
        """双击"""
        lParam = win32api.MAKELONG(x, y)

        # 发送双击消息
        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDBLCLK, win32con.MK_LBUTTON, lParam)
        time.sleep(0.05)
        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, lParam)

    def press_key(self, vk_code):
        """发送按键消息"""
        # 按下
        win32api.PostMessage(self.hwnd, win32con.WM_KEYDOWN, vk_code, 0)
        time.sleep(0.05)

        # 释放
        win32api.PostMessage(self.hwnd, win32con.WM_KEYUP, vk_code, 0)

    def get_window_rect(self):
        """获取窗口位置和大小"""
        rect = win32gui.GetWindowRect(self.hwnd)
        return rect  # (left, top, right, bottom)

    def screen_to_client(self, screen_x, screen_y):
        """
        将屏幕坐标转换为窗口内坐标

        参数:
            screen_x, screen_y: 屏幕绝对坐标

        返回:
            (client_x, client_y): 窗口内相对坐标
        """
        rect = self.get_window_rect()
        client_x = screen_x - rect[0]
        client_y = screen_y - rect[1]
        return (client_x, client_y)


# ============================================
# 方案3: 使用pydirectinput（专为游戏设计）
# ============================================

def install_pydirectinput():
    """
    安装pydirectinput

    pydirectinput是专门为游戏设计的输入库，使用DirectInput
    很多游戏不会屏蔽DirectInput

    安装: pip install pydirectinput
    """
    print("请运行: pip install pydirectinput")
    print("\n使用示例:")
    print("""
import pydirectinput

# 移动鼠标
pydirectinput.moveTo(100, 100)

# 点击
pydirectinput.click()
pydirectinput.click(100, 100)

# 按键
pydirectinput.press('space')
pydirectinput.keyDown('w')
pydirectinput.keyUp('w')
    """)


# ============================================
# 实用工具函数
# ============================================

def find_game_window(keyword):
    """
    查找包含关键词的游戏窗口

    参数:
        keyword: 窗口标题关键词

    返回:
        窗口句柄列表
    """
    windows = []

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if keyword.lower() in title.lower():
                windows.append((hwnd, title))
        return True

    win32gui.EnumWindows(callback, None)
    return windows


def list_all_windows():
    """列出所有可见窗口"""
    print("所有可见窗口:")
    print("-" * 60)

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                rect = win32gui.GetWindowRect(hwnd)
                print(f"句柄: {hwnd}")
                print(f"标题: {title}")
                print(f"位置: {rect}")
                print("-" * 60)
        return True

    win32gui.EnumWindows(callback, None)


# ============================================
# 使用示例
# ============================================

if __name__ == "__main__":
    print("游戏输入高级方案测试")
    print("=" * 60)

    # 示例1: 使用Windows API
    print("\n示例1: Windows API输入")
    print("3秒后点击屏幕中心...")
    time.sleep(3)

    win_input = WindowsInput()
    screen_w, screen_h = win_input.get_screen_size()
    win_input.click(screen_w // 2, screen_h // 2)
    print("点击完成")

    # 示例2: 查找游戏窗口
    print("\n示例2: 查找游戏窗口")
    keyword = input("输入游戏窗口标题关键词（如'地下城'）: ")
    if keyword:
        windows = find_game_window(keyword)
        if windows:
            print(f"\n找到 {len(windows)} 个匹配的窗口:")
            for hwnd, title in windows:
                print(f"  句柄: {hwnd}, 标题: {title}")
        else:
            print("未找到匹配的窗口")

    # 示例3: 使用PostMessage（需要窗口句柄）
    print("\n示例3: PostMessage输入")
    print("提示: 这需要知道游戏窗口标题")
    print("示例代码:")
    print("""
# 假设游戏窗口标题是 "地下城与勇士"
msg_input = WindowMessageInput(window_title="地下城与勇士")

# 点击窗口内坐标 (100, 100)
msg_input.click(100, 100)

# 如果你有屏幕坐标，需要转换
screen_x, screen_y = 500, 300
client_x, client_y = msg_input.screen_to_client(screen_x, screen_y)
msg_input.click(client_x, client_y)
    """)

    # 示例4: 列出所有窗口
    print("\n是否列出所有窗口? (y/n): ", end="")
    if input().lower() == 'y':
        list_all_windows()

    print("\n测试完成!")
