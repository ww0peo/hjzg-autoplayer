"""
安装GUI所需的依赖包
"""

import subprocess
import sys

def install_package(package):
    """安装Python包"""
    print(f"正在安装 {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} 安装成功")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ {package} 安装失败")
        return False

def main():
    print("=" * 60)
    print("安装游戏自动化GUI所需依赖")
    print("=" * 60)

    packages = [
        "keyboard",  # 全局快捷键支持
    ]

    print("\n需要安装的包:")
    for pkg in packages:
        print(f"  - {pkg}")

    print("\n开始安装...\n")

    success_count = 0
    for pkg in packages:
        if install_package(pkg):
            success_count += 1
        print()

    print("=" * 60)
    print(f"安装完成: {success_count}/{len(packages)} 个包安装成功")
    print("=" * 60)

    if success_count == len(packages):
        print("\n✓ 所有依赖安装成功！")
        print("\n运行GUI:")
        print("  python gui_script.py")
        print("\n或者:")
        print("  .venv\\Scripts\\python.exe gui_script.py")
    else:
        print("\n✗ 部分依赖安装失败，请检查错误信息")

    print("\n注意:")
    print("  - keyboard 库需要管理员权限才能注册全局快捷键")
    print("  - 如果快捷键无效，请以管理员身份运行")

if __name__ == "__main__":
    main()
