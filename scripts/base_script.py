"""
脚本基类

所有自定义脚本都应该继承这个类
"""

from abc import ABC, abstractmethod

# 全局脚本注册表
AVAILABLE_SCRIPTS = {}


class BaseScript(ABC):
    """脚本基类"""

    def __init__(self, gui_app):
        """
        初始化脚本

        Args:
            gui_app: GUI应用实例，提供以下方法:
                - gui_app.log(message, level) - 输出日志
                - gui_app.sleep(seconds) - 可中断的睡眠
                - gui_app.is_running - 是否正在运行
                - gui_app.is_paused - 是否暂停
                - gui_app.detector - 屏幕检测器
                - gui_app.game_input - 游戏输入控制器
        """
        self.app = gui_app
        self.run_count = 0

    @classmethod
    def get_all_scripts(cls):
        """获取所有已注册的脚本"""
        return AVAILABLE_SCRIPTS.copy()

    @abstractmethod
    def execute(self):
        """
        执行脚本的主逻辑

        Returns:
            bool: 执行成功返回 True，失败返回 False
        """
        pass

    @abstractmethod
    def get_name(self):
        """
        获取脚本名称

        Returns:
            str: 脚本名称
        """
        pass

    @abstractmethod
    def get_description(self):
        """
        获取脚本描述

        Returns:
            str: 脚本描述
        """
        pass

    def on_start(self):
        """脚本启动时的回调（可选重写）"""
        self.app.log(f"启动脚本: {self.get_name()}", "SUCCESS")

    def on_stop(self):
        """脚本停止时的回调（可选重写）"""
        self.app.log(f"停止脚本: {self.get_name()}", "INFO")

    def on_pause(self):
        """脚本暂停时的回调（可选重写）"""
        pass

    def on_resume(self):
        """脚本恢复时的回调（可选重写）"""
        pass

    # 便捷方法
    def log(self, message, level="INFO"):
        """输出日志"""
        self.app.log(message, level)

    def sleep(self, seconds):
        """可中断的睡眠"""
        return self.app.sleep(seconds)

    @property
    def detector(self):
        """获取检测器"""
        return self.app.detector

    @property
    def game_input(self):
        """获取游戏输入控制器"""
        return self.app.game_input

    @property
    def is_running(self):
        """是否正在运行"""
        return self.app.is_running

    @property
    def is_paused(self):
        """是否暂停"""
        return self.app.is_paused
