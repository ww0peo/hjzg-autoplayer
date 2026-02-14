"""
游戏操作工具函数

提供通用的游戏操作辅助函数，包括窗口管理、对象检测、点击操作等
"""

import time
import win32gui
import win32con
import pyautogui


# 设置PyAutoGUI的安全延迟
pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True


def sleep(seconds):
    """睡眠函数"""
    time.sleep(seconds)


def activate_game_window(window_title=None):
    """
    激活游戏窗口（确保游戏在前台）

    参数:
        window_title: 窗口标题关键词（如 'Torchlight: Infinite'）

    返回:
        bool: 是否成功激活窗口
    """
    if window_title:
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                sleep(0.2)
                return True
        except Exception:
            pass
    return False


def get_pos_by_name(detector, name):
    """
    检测屏幕上的对象并返回其中心坐标

    参数:
        detector: ScreenDetector实例
        name: 对象名称

    返回:
        tuple: (x, y) 中心坐标
    """
    xy = detector.get_center_by_name(name=name)
    while not xy:
        sleep(1)
        xy = detector.get_center_by_name(name=name)
    return xy


def press_a():
    """使用A键拾取物品"""
    for _ in range(5):
        pyautogui.press('a')
        sleep(0.5)


def pick_up_items(detector, name, game_input=None):
    """
    拾取屏幕上的所有物品

    参数:
        detector: ScreenDetector实例
        name: 物品对象名称
        game_input: GameInput实例（可选，如果不提供则使用默认点击方式）
    """
    press_a()
    sleep(1)
    items = detector.get_all_centers_by_name(name)
    while items:
        if game_input:
            game_input.click(items[0][0], items[0][1])
        else:
            pyautogui.click(items[0][0], items[0][1])
        press_a()
        sleep(1)
        items = detector.get_all_centers_by_name(name)


def click_pos(pos, click_type='single', duration=0.2, use_api=True, game_input=None):
    """
    点击指定位置

    参数:
        pos: 坐标 (x, y)
        click_type: 点击类型
            - 'single': 单击
            - 'double': 双击
            - 'right': 右键
        duration: 鼠标移动时间（秒，仅PyAutoGUI有效）
        use_api: 是否使用Windows API（True=使用game_input，False=使用PyAutoGUI）
        game_input: GameInput实例（当use_api=True时必须提供）
    """
    if use_api and game_input:
        # 使用Windows API（绕过游戏保护）
        game_input.move_mouse(pos[0], pos[1])
        sleep(0.15)

        if click_type == 'double':
            game_input.double_click()
        elif click_type == 'right':
            game_input.click(button="right")
        else:
            game_input.click()
    else:
        # 使用PyAutoGUI
        pyautogui.moveTo(pos[0], pos[1], duration=duration)
        sleep(0.15)

        if click_type == 'double':
            pyautogui.doubleClick()
        elif click_type == 'right':
            pyautogui.click(button='right')
        else:
            pyautogui.click()

    sleep(0.2)
