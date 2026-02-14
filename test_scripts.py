"""
测试脚本系统
"""
from scripts.base_script import BaseScript
from scripts.dungeon_script import DungeonScript

def test_script_registry():
    """测试脚本注册"""
    print("测试脚本注册系统...")

    # 获取所有注册的脚本
    scripts = BaseScript.get_all_scripts()

    print(f"\n已注册的脚本数量: {len(scripts)}")
    print("\n脚本列表:")

    # 创建一个模拟的GUI应用对象
    class MockGUI:
        def log(self, msg, level="INFO"):
            pass
        def sleep(self, seconds):
            return True
        is_running = True
        is_paused = False
        detector = None
        game_input = None

    for name, script_class in scripts.items():
        # 创建临时实例获取描述
        temp_instance = script_class(MockGUI())
        description = temp_instance.get_description()
        print(f"  - {name}: {description}")

    print("\n✓ 脚本注册测试通过")

def test_script_instantiation():
    """测试脚本实例化"""
    print("\n测试脚本实例化...")

    # 创建一个模拟的GUI应用对象
    class MockGUI:
        def log(self, msg, level="INFO"):
            pass
        def sleep(self, seconds):
            return True
        is_running = True
        is_paused = False
        detector = None
        game_input = None

    scripts = BaseScript.get_all_scripts()

    for name, script_class in scripts.items():
        try:
            instance = script_class(MockGUI())
            description = instance.get_description()
            print(f"  ✓ {name} 实例化成功: {description}")
        except Exception as e:
            print(f"  ✗ {name} 实例化失败: {e}")
            raise

    print("\n✓ 脚本实例化测试通过")

if __name__ == "__main__":
    print("=" * 60)
    print("开始测试脚本系统")
    print("=" * 60)

    test_script_registry()
    test_script_instantiation()

    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)
