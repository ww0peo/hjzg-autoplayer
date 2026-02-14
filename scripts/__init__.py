"""
游戏自动化脚本模块

所有脚本都应该继承 BaseScript 类
"""

from .base_script import BaseScript
from .dungeon_script import DungeonScript
from .example_script import ExampleScript

# 注册所有可用的脚本
AVAILABLE_SCRIPTS = {
    "副本刷图": DungeonScript,
    "示例脚本": ExampleScript,
    # 在这里添加新的脚本
    # "日常任务": DailyQuestScript,
    # "自动钓鱼": FishingScript,
}

__all__ = ['BaseScript', 'DungeonScript', 'AVAILABLE_SCRIPTS']
