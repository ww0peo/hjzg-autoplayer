"""
副本刷图脚本

自动执行副本刷图流程
"""

from .base_script import BaseScript
from game_utils import get_pos_by_name, click_pos, pick_up_items


class DungeonScript(BaseScript):
    """副本刷图脚本"""

    def get_name(self):
        return "副本刷图"

    def get_description(self):
        return "自动前往传送门、进入副本、拾取物品并退出"

    def execute(self):
        """执行副本刷图流程"""
        try:
            # 步骤1: 前往传送门
            self.log("\n[步骤1] 前往传送门...", "INFO")
            portal2_xy = get_pos_by_name(self.detector, 'portal2')
            if portal2_xy and self.is_running:
                click_pos(portal2_xy, click_type='double', duration=0.3)
                if not self.sleep(1):
                    return False

                # 等待到达传送门
                button1_xy = self.detector.get_center_by_name(name='button1')
                retry_count = 0
                while not button1_xy and retry_count < 10 and self.is_running:
                    self.log(f"等待到达传送门... (尝试 {retry_count + 1}/10)", "DEBUG")
                    portal2_xy = get_pos_by_name(self.detector, 'portal2')
                    click_pos(portal2_xy, click_type='double', duration=0.3)
                    if not self.sleep(2):
                        return False
                    button1_xy = self.detector.get_center_by_name(name='button1')
                    retry_count += 1

            # 步骤2: 进入传送门
            self.log("\n[步骤2] 进入传送门...", "INFO")
            button1_xy = get_pos_by_name(self.detector, 'button1')
            if button1_xy and self.is_running:
                click_pos(button1_xy, click_type='single')
                if not self.sleep(1):
                    return False

            dungeon_xy = get_pos_by_name(self.detector, 'dungeon')
            if dungeon_xy and self.is_running:
                click_pos(dungeon_xy, click_type='single')
                if not self.sleep(1):
                    return False

            startButton_xy = get_pos_by_name(self.detector, 'startButton')
            if startButton_xy and self.is_running:
                click_pos(startButton_xy, click_type='single')
                if not self.sleep(2):
                    return False

            # 步骤3: 闪现到副本中心
            self.log("\n[步骤3] 闪现到副本中心...", "INFO")
            screen_width, screen_height = self.game_input.get_screen_size()
            screen_center = (screen_width // 2, screen_height // 5)

            person_xy = get_pos_by_name(self.detector, 'person')
            if person_xy and self.is_running:
                self.log(f"检测到人物位置: {person_xy}", "DEBUG")
                if not self.sleep(3):
                    return False

            if self.is_running:
                self.game_input.move_mouse(screen_center[0], screen_center[1])
                if not self.sleep(0.2):
                    return False
                self.game_input.right_click()
                self.log(f"右键闪现到: {screen_center}", "DEBUG")
                if not self.sleep(3):
                    return False

            # 步骤4: 拾取物品并退出
            self.log("\n[步骤4] 拾取物品并退出副本...", "INFO")
            portal1_xy = get_pos_by_name(self.detector, 'portal1')
            if portal1_xy and self.is_running:
                pick_up_items(self.detector, 'props')
                if not self.sleep(1):
                    return False

                portal1_xy = get_pos_by_name(self.detector, 'portal1')
                click_pos(portal1_xy, click_type='double', duration=0.3)
                if not self.sleep(1):
                    return False

            button2_xy = self.detector.get_center_by_name(name='button2')
            while not button2_xy and self.is_running:
                portal1_xy = get_pos_by_name(self.detector, 'portal1')
                click_pos((portal1_xy[0], portal1_xy[1] + 20), click_type='double', duration=0.3)
                if not self.sleep(1):
                    return False
                button2_xy = self.detector.get_center_by_name(name='button2')
                if button2_xy and self.is_running:
                    click_pos(button2_xy, click_type='single')
                    if not self.sleep(1):
                        return False
                    
            return True

        except Exception as e:
            self.log(f"执行步骤出错: {e}", "ERROR")
            return False


# 注册脚本
from .base_script import AVAILABLE_SCRIPTS
AVAILABLE_SCRIPTS['dungeon'] = DungeonScript
