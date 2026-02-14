"""
测试不同的游戏输入方法

这个脚本会测试3种不同的输入方法，帮你找到在游戏中有效的方法
"""

import time
import ctypes
import pyautogui
import win32api
import win32con
import win32gui


class InputTester:
    """测试不同的输入方法"""

    def __init__(self):
        self.user32 = ctypes.windll.user32

    def get_screen_size(self):
        return self.user32.GetSystemMetrics(0), self.user32.GetSystemMetrics(1)

    def test_method_1_pyautogui(self, x, y):
        """方法1: PyAutoGUI（最简单，但容易被检测）"""
        print("\n[方法1] 使用 PyAutoGUI")
        print(f"  - 移动到: ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(0.2)
        print("  - 点击")
        pyautogui.click()
        print("  ✓ 完成")

    def test_method_2_mouse_event(self, x, y):
        """方法2: Windows mouse_event API（中等难度检测）"""
        print("\n[方法2] 使用 Windows mouse_event API")
        screen_width, screen_height = self.get_screen_size()

        # 转换为绝对坐标
        abs_x = int(x * 65535 / screen_width)
        abs_y = int(y * 65535 / screen_height)

        print(f"  - 移动到: ({x}, {y})")
        self.user32.mouse_event(0x8001, abs_x, abs_y, 0, 0)  # MOVE + ABSOLUTE
        time.sleep(0.2)

        print("  - 按下左键")
        self.user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
        time.sleep(0.05)

        print("  - 释放左键")
        self.user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
        print("  ✓ 完成")

    def test_method_3_sendinput(self, x, y):
        """方法3: Windows SendInput API（最难检测）"""
        print("\n[方法3] 使用 Windows SendInput API")

        # 定义INPUT结构
        PUL = ctypes.POINTER(ctypes.c_ulong)

        class MouseInput(ctypes.Structure):
            _fields_ = [
                ("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)
            ]

        class Input_I(ctypes.Union):
            _fields_ = [("mi", MouseInput)]

        class Input(ctypes.Structure):
            _fields_ = [
                ("type", ctypes.c_ulong),
                ("ii", Input_I)
            ]

        screen_width, screen_height = self.get_screen_size()

        # 转换为绝对坐标
        abs_x = int(x * 65535 / screen_width)
        abs_y = int(y * 65535 / screen_height)

        # 移动鼠标
        print(f"  - 移动到: ({x}, {y})")
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(abs_x, abs_y, 0, 0x8001, 0, ctypes.pointer(extra))
        command = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))
        time.sleep(0.2)

        # 按下左键
        print("  - 按下左键")
        ii_.mi = MouseInput(0, 0, 0, 0x0002, 0, ctypes.pointer(extra))
        command = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))
        time.sleep(0.05)

        # 释放左键
        print("  - 释放左键")
        ii_.mi = MouseInput(0, 0, 0, 0x0004, 0, ctypes.pointer(extra))
        command = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))
        print("  ✓ 完成")

    def test_method_4_postmessage(self, window_title, x, y):
        """方法4: PostMessage（直接发送消息到窗口）"""
        print("\n[方法4] 使用 PostMessage")

        # 查找窗口
        hwnd = win32gui.FindWindow(None, window_title)
        if not hwnd:
            print(f"  ✗ 未找到窗口: {window_title}")
            return

        # 获取窗口位置
        rect = win32gui.GetWindowRect(hwnd)
        client_x = x - rect[0]
        client_y = y - rect[1]

        print(f"  - 窗口句柄: {hwnd}")
        print(f"  - 屏幕坐标: ({x}, {y})")
        print(f"  - 窗口内坐标: ({client_x}, {client_y})")

        # 构造lParam
        lParam = win32api.MAKELONG(client_x, client_y)

        print("  - 发送 WM_LBUTTONDOWN")
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        time.sleep(0.05)

        print("  - 发送 WM_LBUTTONUP")
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
        print("  ✓ 完成")


def find_windows_by_keyword(keyword):
    """查找包含关键词的窗口"""
    windows = []

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if keyword.lower() in title.lower():
                windows.append((hwnd, title))
        return True

    win32gui.EnumWindows(callback, None)
    return windows


def main():
    print("=" * 60)
    print("游戏输入方法测试工具")
    print("=" * 60)

    # 查找游戏窗口
    print("\n请输入游戏窗口标题关键词（如'地下城'、'DNF'等）:")
    keyword = input("> ").strip()

    if keyword:
        windows = find_windows_by_keyword(keyword)
        if windows:
            print(f"\n找到 {len(windows)} 个匹配的窗口:")
            for i, (hwnd, title) in enumerate(windows, 1):
                print(f"  {i}. {title}")

            if len(windows) == 1:
                window_title = windows[0][1]
                print(f"\n将使用窗口: {window_title}")
            else:
                choice = int(input("\n请选择窗口编号: ")) - 1
                window_title = windows[choice][1]
        else:
            print(f"\n未找到包含'{keyword}'的窗口")
            window_title = None
    else:
        window_title = None

    # 获取测试坐标
    print("\n" + "=" * 60)
    print("请将鼠标移动到游戏中要测试点击的位置")
    print("5秒后将记录鼠标位置...")
    print("=" * 60)

    for i in range(5, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print()

    # 获取当前鼠标位置
    x, y = pyautogui.position()
    print(f"\n记录的坐标: ({x}, {y})")

    # 创建测试器
    tester = InputTester()

    # 测试所有方法
    print("\n" + "=" * 60)
    print("开始测试（每个方法间隔3秒）")
    print("请观察游戏中是否有反应")
    print("=" * 60)

    time.sleep(2)

    # 测试方法1
    tester.test_method_1_pyautogui(x, y)
    time.sleep(3)

    # 测试方法2
    tester.test_method_2_mouse_event(x, y)
    time.sleep(3)

    # 测试方法3
    tester.test_method_3_sendinput(x, y)
    time.sleep(3)

    # 测试方法4（需要窗口标题）
    if window_title:
        tester.test_method_4_postmessage(window_title, x, y)
        time.sleep(3)

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n请告诉我哪个方法在游戏中有效:")
    print("  1. PyAutoGUI")
    print("  2. mouse_event API")
    print("  3. SendInput API")
    print("  4. PostMessage")
    print("\n如果都无效，可能需要:")
    print("  - 使用管理员权限运行")
    print("  - 尝试 pydirectinput 库")
    print("  - 检查游戏是否有反作弊保护")


if __name__ == "__main__":
    main()
