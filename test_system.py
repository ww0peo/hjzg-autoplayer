"""测试脚本系统"""
from scripts.base_script import BaseScript
from scripts import AVAILABLE_SCRIPTS
from scripts.example_script import ExampleScript
from gui_script import GameAutomationGUI
import tkinter as tk


def test_script_registration():
    """测试脚本注册系统"""
    print("=" * 60)
    print("测试脚本注册系统")
    print("=" * 60)

    # 方式1: 通过 BaseScript 自动注册
    print("\n【方式1】BaseScript 自动注册的脚本:")
    auto_scripts = BaseScript.get_all_scripts()
    print(f"数量: {len(auto_scripts)}")
    for name, script_class in auto_scripts.items():
        print(f"  - {name}: {script_class.__name__}")

    # 方式2: 通过 AVAILABLE_SCRIPTS 字典
    print("\n【方式2】AVAILABLE_SCRIPTS 字典中的脚本:")
    print(f"数量: {len(AVAILABLE_SCRIPTS)}")
    for name, script_class in AVAILABLE_SCRIPTS.items():
        print(f"  - {name}: {script_class.__name__}")

    # 测试 ExampleScript 是否被注册
    print("\n【测试】ExampleScript 注册状态:")
    root = tk.Tk()
    app = GameAutomationGUI(root)
    example_name = ExampleScript(app).get_name()
    if example_name in auto_scripts:
        print(f"✓ '{example_name}' 已通过自动注册")
    else:
        print(f"✗ '{example_name}' 未自动注册")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_script_registration()
