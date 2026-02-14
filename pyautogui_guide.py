"""
PyAutoGUI 常用API完整指南

安装: pip install pyautogui
文档: https://pyautogui.readthedocs.io/
"""

import pyautogui
import time


# ============================================
# 1. 基础设置
# ============================================

# 设置每次操作后的暂停时间（秒）
pyautogui.PAUSE = 0.1  # 推荐设置，防止操作过快

# 启用安全模式（鼠标移到左上角可紧急停止）
pyautogui.FAILSAFE = True

# 获取屏幕尺寸
screen_width, screen_height = pyautogui.size()
print(f"屏幕尺寸: {screen_width}x{screen_height}")


# ============================================
# 2. 鼠标控制
# ============================================

# 2.1 获取鼠标位置
x, y = pyautogui.position()
print(f"当前鼠标位置: ({x}, {y})")

# 2.2 移动鼠标
pyautogui.moveTo(100, 100)              # 移动到绝对坐标 (100, 100)
pyautogui.moveTo(100, 100, duration=1)  # 1秒内平滑移动到 (100, 100)
pyautogui.move(10, 20)                  # 相对移动（向右10，向下20）
pyautogui.moveRel(10, 20)               # 同上

# 2.3 鼠标点击
pyautogui.click()                       # 在当前位置单击左键
pyautogui.click(100, 100)               # 移动到 (100, 100) 并单击
pyautogui.click(button='left')          # 左键点击
pyautogui.click(button='right')         # 右键点击
pyautogui.click(button='middle')        # 中键点击
pyautogui.click(clicks=2)               # 双击
pyautogui.click(clicks=3, interval=0.1) # 三击，间隔0.1秒

# 2.4 快捷点击方法
pyautogui.doubleClick()                 # 双击
pyautogui.tripleClick()                 # 三击
pyautogui.rightClick()                  # 右键点击
pyautogui.middleClick()                 # 中键点击

# 2.5 鼠标按下和释放
pyautogui.mouseDown()                   # 按下左键
pyautogui.mouseUp()                     # 释放左键
pyautogui.mouseDown(button='right')     # 按下右键
pyautogui.mouseUp(button='right')       # 释放右键

# 2.6 拖拽
pyautogui.drag(100, 0, duration=0.5)    # 向右拖拽100像素
pyautogui.dragTo(200, 200, duration=1)  # 拖拽到 (200, 200)

# 2.7 滚动
pyautogui.scroll(10)                    # 向上滚动10个单位
pyautogui.scroll(-10)                   # 向下滚动10个单位
pyautogui.hscroll(10)                   # 水平滚动（部分系统支持）


# ============================================
# 3. 键盘控制
# ============================================

# 3.1 输入文本
pyautogui.write('Hello World!')         # 输入文本
pyautogui.write('你好', interval=0.1)    # 每个字符间隔0.1秒

# 3.2 按键操作
pyautogui.press('enter')                # 按下并释放回车键
pyautogui.press('esc')                  # 按ESC键
pyautogui.press('f1')                   # 按F1键

# 3.3 按键组合
pyautogui.hotkey('ctrl', 'c')           # Ctrl+C（复制）
pyautogui.hotkey('ctrl', 'v')           # Ctrl+V（粘贴）
pyautogui.hotkey('ctrl', 'shift', 's')  # Ctrl+Shift+S
pyautogui.hotkey('alt', 'tab')          # Alt+Tab（切换窗口）

# 3.4 按下和释放
pyautogui.keyDown('shift')              # 按下Shift键
pyautogui.press('a')                    # 按A键（此时是大写A）
pyautogui.keyUp('shift')                # 释放Shift键

# 3.5 常用按键名称
"""
字母: 'a' - 'z'
数字: '0' - '9'
功能键: 'f1' - 'f12'
方向键: 'up', 'down', 'left', 'right'
特殊键: 'enter', 'esc', 'space', 'tab', 'backspace', 'delete'
        'home', 'end', 'pageup', 'pagedown', 'insert'
修饰键: 'shift', 'ctrl', 'alt', 'win' (Windows键)
        'command' (Mac), 'option' (Mac)
"""


# ============================================
# 4. 屏幕截图
# ============================================

# 4.1 全屏截图
screenshot = pyautogui.screenshot()
screenshot.save('screenshot.png')

# 4.2 区域截图
region_screenshot = pyautogui.screenshot(region=(0, 0, 300, 400))
# region=(x, y, width, height)

# 4.3 截图并转为numpy数组
import numpy as np
screenshot_array = np.array(pyautogui.screenshot())


# ============================================
# 5. 图像识别与定位
# ============================================

# 5.1 在屏幕上查找图片
try:
    location = pyautogui.locateOnScreen('button.png')
    if location:
        print(f"找到图片位置: {location}")
        # location = Box(left=x, top=y, width=w, height=h)
except pyautogui.ImageNotFoundException:
    print("未找到图片")

# 5.2 查找图片中心点
center = pyautogui.locateCenterOnScreen('button.png')
if center:
    print(f"图片中心点: {center}")
    pyautogui.click(center)  # 点击图片中心

# 5.3 查找所有匹配的图片
all_locations = list(pyautogui.locateAllOnScreen('icon.png'))
print(f"找到 {len(all_locations)} 个匹配")

# 5.4 设置置信度（0.0-1.0）
location = pyautogui.locateOnScreen('button.png', confidence=0.8)

# 5.5 灰度匹配（更快）
location = pyautogui.locateOnScreen('button.png', grayscale=True)


# ============================================
# 6. 消息框
# ============================================

# 6.1 警告框
pyautogui.alert('这是一个警告框', '标题')

# 6.2 确认框
result = pyautogui.confirm('确定要继续吗?', buttons=['确定', '取消'])
print(f"用户选择: {result}")

# 6.3 输入框
name = pyautogui.prompt('请输入你的名字:')
print(f"输入的名字: {name}")

# 6.4 密码框
password = pyautogui.password('请输入密码:')


# ============================================
# 7. 实用工具函数
# ============================================

# 7.1 暂停
time.sleep(1)  # 暂停1秒

# 7.2 判断坐标是否在屏幕内
is_on_screen = pyautogui.onScreen(100, 100)
print(f"坐标是否在屏幕内: {is_on_screen}")

# 7.3 获取像素颜色
pixel_color = pyautogui.pixel(100, 100)
print(f"坐标(100, 100)的颜色: {pixel_color}")  # RGB元组

# 7.4 像素匹配
if pyautogui.pixelMatchesColor(100, 100, (255, 0, 0)):
    print("该像素是红色")


# ============================================
# 8. 游戏自动化常用模式
# ============================================

def game_click(x, y, click_type='single', duration=0.2):
    """
    游戏点击（更可靠）

    参数:
        x, y: 坐标
        click_type: 'single', 'double', 'right'
        duration: 移动时间
    """
    # 平滑移动
    pyautogui.moveTo(x, y, duration=duration)
    time.sleep(0.1)  # 移动后等待

    # 点击
    if click_type == 'double':
        pyautogui.doubleClick()
    elif click_type == 'right':
        pyautogui.rightClick()
    else:
        pyautogui.click()

    time.sleep(0.2)  # 点击后等待


def find_and_click(image_path, confidence=0.8):
    """查找图片并点击"""
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            pyautogui.click(location)
            return True
    except:
        pass
    return False


def wait_for_image(image_path, timeout=10, confidence=0.8):
    """等待图片出现"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                return location
        except:
            pass
        time.sleep(0.5)
    return None


def spam_click(x, y, count=10, interval=0.1):
    """连续点击"""
    for i in range(count):
        pyautogui.click(x, y)
        time.sleep(interval)


def hold_and_drag(start_x, start_y, end_x, end_y, duration=1):
    """按住并拖拽"""
    pyautogui.moveTo(start_x, start_y)
    pyautogui.mouseDown()
    time.sleep(0.1)
    pyautogui.moveTo(end_x, end_y, duration=duration)
    time.sleep(0.1)
    pyautogui.mouseUp()


# ============================================
# 9. 游戏常用技巧
# ============================================

# 9.1 激活游戏窗口（Windows）
def activate_window(window_title):
    """激活指定窗口"""
    try:
        import win32gui
        import win32con

        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.2)
            return True
    except:
        pass
    return False


# 9.2 循环检测并点击
def auto_click_loop(image_path, interval=1, max_clicks=10):
    """自动检测并点击"""
    clicks = 0
    while clicks < max_clicks:
        if find_and_click(image_path):
            print(f"点击成功 ({clicks + 1}/{max_clicks})")
            clicks += 1
        time.sleep(interval)


# 9.3 技能释放（游戏常用）
def cast_skill(key, target_x=None, target_y=None):
    """释放技能"""
    if target_x and target_y:
        # 先移动鼠标到目标位置
        pyautogui.moveTo(target_x, target_y, duration=0.1)
        time.sleep(0.05)

    # 按技能键
    pyautogui.press(key)
    time.sleep(0.1)


# 9.4 拾取物品
def pickup_items(item_positions):
    """批量拾取物品"""
    for pos in item_positions:
        pyautogui.moveTo(pos[0], pos[1], duration=0.2)
        time.sleep(0.05)
        pyautogui.click()
        time.sleep(0.1)


# ============================================
# 10. 调试工具
# ============================================

def display_mouse_position():
    """实时显示鼠标位置（按Ctrl+C停止）"""
    print("移动鼠标查看坐标，按Ctrl+C停止")
    try:
        while True:
            x, y = pyautogui.position()
            pixel = pyautogui.pixel(x, y)
            print(f"X: {x:4d} Y: {y:4d} RGB: {pixel}", end='\r')
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n已停止")


# ============================================
# 使用示例
# ============================================

if __name__ == "__main__":
    print("PyAutoGUI 常用API示例")
    print("=" * 50)

    # 示例1: 基础点击
    print("\n示例1: 3秒后点击屏幕中心")
    time.sleep(3)
    center_x = screen_width // 2
    center_y = screen_height // 2
    pyautogui.click(center_x, center_y)

    # 示例2: 输入文本
    print("\n示例2: 输入文本（请先打开文本编辑器）")
    time.sleep(3)
    pyautogui.write('Hello from PyAutoGUI!')

    # 示例3: 截图
    print("\n示例3: 截图保存")
    screenshot = pyautogui.screenshot()
    screenshot.save('test_screenshot.png')
    print("截图已保存为 test_screenshot.png")

    # 示例4: 显示鼠标位置（取消注释使用）
    # display_mouse_position()

    print("\n所有示例执行完成!")
