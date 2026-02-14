"""
示例脚本模板

复制此文件并修改为你自己的脚本
"""

from .base_script import BaseScript
from game_utils import get_pos_by_name, click_pos


class ExampleScript(BaseScript):
    """示例脚本"""

    def get_name(self):
        """返回脚本名称"""
        return "示例脚本"

    def get_description(self):
        """返回脚本描述"""
        return "这是一个示例脚本模板"

    def execute(self):
        """
        执行脚本的主逻辑

        Returns:
            bool: 执行成功返回 True，失败返回 False
        """
        try:
            # 在这里编写你的脚本逻辑

            # 示例1: 输出日志
            self.log("开始执行示例脚本", "INFO")

            # 示例2: 检测屏幕对象
            obj_xy = get_pos_by_name(self.detector, 'object_name')
            if obj_xy and self.is_running:
                self.log(f"检测到对象位置: {obj_xy}", "DEBUG")

                # 示例3: 点击位置
                click_pos(obj_xy, click_type='single')

                # 示例4: 等待（可被暂停/停止中断）
                if not self.sleep(1):
                    return False

            # 示例5: 使用游戏输入控制器
            # self.game_input.move_mouse(100, 100)
            # self.game_input.left_click()
            # self.game_input.right_click()
            # self.game_input.press_key('space')

            # 示例6: 获取屏幕尺寸
            # screen_width, screen_height = self.game_input.get_screen_size()

            self.log("示例脚本执行完成", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"执行出错: {e}", "ERROR")
            return False

    def on_start(self):
        """脚本启动时的回调（可选）"""
        super().on_start()
        self.log("示例脚本启动回调", "DEBUG")

    def on_stop(self):
        """脚本停止时的回调（可选）"""
        super().on_stop()
        self.log("示例脚本停止回调", "DEBUG")


# 注册脚本
from .base_script import AVAILABLE_SCRIPTS
AVAILABLE_SCRIPTS['example'] = ExampleScript