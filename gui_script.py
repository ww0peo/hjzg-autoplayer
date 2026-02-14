"""
游戏自动化脚本 - 图形化界面版本

功能:
- 启动/暂停/停止按钮
- 全局快捷键: F10=启动, F11=暂停, F12=停止
- 实时日志显示
- 状态指示器
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime
import sys
import keyboard  # 需要安装: pip install keyboard

# 导入原脚本的功能
from game_utils import activate_game_window
from game_input_advanced import WindowsInput as GameInput
from screen_detector import ScreenDetector

# 导入脚本模块
from scripts.base_script import BaseScript


class GameAutomationGUI:
    """游戏自动化图形界面"""

    def __init__(self, root):
        self.root = root
        self.root.title("游戏自动化控制台")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # 状态变量
        self.is_running = False
        self.is_paused = False
        self.script_thread = None
        self.detector = None
        self.game_input = GameInput()
        self.current_script = None  # 当前运行的脚本实例
        self.run_count = 0  # 运行次数计数器

        # 配置变量
        self.window_title = tk.StringVar(value="Torchlight: Infinite")
        self.model_path = tk.StringVar(value="hjzgv1.pt")
        self.conf_threshold = tk.DoubleVar(value=0.5)

        # 获取所有可用脚本
        available_scripts = BaseScript.get_all_scripts()
        self.selected_script = tk.StringVar(value=list(available_scripts.keys())[0] if available_scripts else "")

        # 创建界面
        self.create_widgets()

        # 注册全局快捷键
        self.register_hotkeys()

        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """创建界面组件"""

        # ===== 顶部配置区 =====
        config_frame = ttk.LabelFrame(self.root, text="配置", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        # 窗口标题
        ttk.Label(config_frame, text="游戏窗口标题:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.window_title, width=30).grid(row=0, column=1, padx=5, pady=2)

        # 模型路径
        ttk.Label(config_frame, text="模型路径:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.model_path, width=30).grid(row=1, column=1, padx=5, pady=2)

        # 置信度
        ttk.Label(config_frame, text="置信度阈值:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(config_frame, from_=0.1, to=1.0, variable=self.conf_threshold,
                  orient=tk.HORIZONTAL, length=200).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(config_frame, textvariable=self.conf_threshold).grid(row=2, column=2, padx=5, pady=2)

        # 脚本选择
        ttk.Label(config_frame, text="选择脚本:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        script_combo = ttk.Combobox(config_frame, textvariable=self.selected_script,
                                     values=list(BaseScript.get_all_scripts().keys()),
                                     state='readonly', width=28)
        script_combo.grid(row=3, column=1, padx=5, pady=2)
        script_combo.bind('<<ComboboxSelected>>', self.on_script_changed)

        # ===== 控制按钮区 =====
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 启动按钮
        self.start_btn = ttk.Button(
            control_frame,
            text="▶ 启动 (F10)",
            command=self.start_script,
            width=20
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        # 暂停按钮
        self.pause_btn = ttk.Button(
            control_frame,
            text="⏸ 暂停 (F11)",
            command=self.pause_script,
            width=20,
            state=tk.DISABLED
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        # 停止按钮
        self.stop_btn = ttk.Button(
            control_frame,
            text="⏹ 停止 (F12)",
            command=self.stop_script,
            width=20,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # ===== 状态指示器 =====
        status_frame = ttk.Frame(self.root, padding=5)
        status_frame.pack(fill=tk.X, padx=10)

        ttk.Label(status_frame, text="状态:").pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(
            status_frame,
            text="● 未启动",
            foreground="gray",
            font=("Arial", 10, "bold")
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

        # 运行次数
        self.run_count_label = ttk.Label(status_frame, text="运行次数: 0")
        self.run_count_label.pack(side=tk.RIGHT, padx=5)

        # ===== 日志显示区 =====
        log_frame = ttk.LabelFrame(self.root, text="运行日志", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            height=20,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 配置日志颜色标签
        self.log_text.tag_config("INFO", foreground="black")
        self.log_text.tag_config("SUCCESS", foreground="green")
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("DEBUG", foreground="blue")

        # ===== 底部提示 =====
        hint_frame = ttk.Frame(self.root, padding=5)
        hint_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(
            hint_frame,
            text="💡 提示: F10=启动 | F11=暂停 | F12=停止 | 鼠标移到左上角可紧急停止",
            foreground="gray",
            font=("Arial", 8)
        ).pack()

    def register_hotkeys(self):
        """注册全局快捷键"""
        try:
            keyboard.add_hotkey('f10', self.start_script)
            keyboard.add_hotkey('f11', self.pause_script)
            keyboard.add_hotkey('f12', self.stop_script)
            self.log("已注册全局快捷键: F10=启动, F11=暂停, F12=停止", "SUCCESS")
        except Exception as e:
            self.log(f"注册快捷键失败: {e}", "ERROR")
            self.log("提示: 可能需要管理员权限", "WARNING")

    def on_script_changed(self, event=None):
        """脚本选择改变时的回调"""
        script_name = self.selected_script.get()
        available_scripts = BaseScript.get_all_scripts()
        if script_name in available_scripts:
            script_class = available_scripts[script_name]
            # 创建临时实例获取描述
            temp_instance = script_class(self)
            description = temp_instance.get_description()
            self.log(f"已选择脚本: {script_name} - {description}", "INFO")

    def log(self, message, level="INFO"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_message, level)
        self.log_text.see(tk.END)  # 自动滚动到底部

    def update_status(self, text, color):
        """更新状态指示器"""
        self.status_label.config(text=f"● {text}", foreground=color)

    def start_script(self):
        """启动脚本"""
        if self.is_running:
            if self.is_paused:
                # 从暂停恢复
                self.is_paused = False
                self.update_status("运行中", "green")
                self.pause_btn.config(text="⏸ 暂停 (F11)")
                self.log("脚本已恢复", "SUCCESS")
            else:
                self.log("脚本已在运行中", "WARNING")
            return

        # 启动新线程运行脚本
        self.is_running = True
        self.is_paused = False

        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)

        self.update_status("运行中", "green")
        self.log("=" * 50, "INFO")
        self.log("脚本启动", "SUCCESS")
        self.log("=" * 50, "INFO")

        self.script_thread = threading.Thread(target=self.run_script, daemon=True)
        self.script_thread.start()

    def pause_script(self):
        """暂停/恢复脚本"""
        if not self.is_running:
            self.log("脚本未运行", "WARNING")
            return

        if self.is_paused:
            # 恢复
            self.is_paused = False
            self.update_status("运行中", "green")
            self.pause_btn.config(text="⏸ 暂停 (F11)")
            self.log("脚本已恢复", "SUCCESS")
        else:
            # 暂停
            self.is_paused = True
            self.update_status("已暂停", "orange")
            self.pause_btn.config(text="▶ 恢复 (F11)")
            self.log("脚本已暂停", "WARNING")

    def stop_script(self):
        """停止脚本"""
        if not self.is_running:
            self.log("脚本未运行", "WARNING")
            return

        self.is_running = False
        self.is_paused = False

        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="⏸ 暂停 (F11)")
        self.stop_btn.config(state=tk.DISABLED)

        self.update_status("已停止", "red")
        self.log("=" * 50, "INFO")
        self.log("脚本已停止", "ERROR")
        self.log("=" * 50, "INFO")

    def sleep(self, seconds):
        """可中断的睡眠"""
        start_time = time.time()
        while time.time() - start_time < seconds:
            if not self.is_running:
                return False
            while self.is_paused:
                time.sleep(0.1)
                if not self.is_running:
                    return False
            time.sleep(0.1)
        return True

    def run_script(self):
        """运行主脚本逻辑"""
        try:
            # 初始化检测器
            self.log(f"加载模型: {self.model_path.get()}", "INFO")
            self.detector = ScreenDetector(
                model_path=self.model_path.get(),
                conf=self.conf_threshold.get()
            )
            self.log("模型加载成功", "SUCCESS")

            # 激活游戏窗口
            window_title = self.window_title.get()
            if window_title:
                self.log(f"激活游戏窗口: {window_title}", "INFO")
                if activate_game_window(window_title):
                    self.log("窗口激活成功", "SUCCESS")
                else:
                    self.log("窗口激活失败，继续执行", "WARNING")

            # 初始化选定的脚本
            script_name = self.selected_script.get()
            available_scripts = BaseScript.get_all_scripts()
            if script_name not in available_scripts:
                self.log(f"未找到脚本: {script_name}", "ERROR")
                return

            script_class = available_scripts[script_name]
            self.current_script = script_class(self)
            self.log(f"已加载脚本: {script_name}", "SUCCESS")
            self.log(f"脚本描述: {self.current_script.get_description()}", "INFO")

            if not self.sleep(2):
                return

            # 主循环
            while self.is_running:
                self.run_count += 1
                self.run_count_label.config(text=f"运行次数: {self.run_count}")
                self.log(f"\n>>> 开始第 {self.run_count} 次运行 <<<", "SUCCESS")

                # 执行脚本
                if not self.current_script.execute():
                    break

                self.log(f"<<< 第 {self.run_count} 次运行完成 >>>\n", "SUCCESS")

                # 等待下一次循环
                if not self.sleep(2):
                    break

        except Exception as e:
            self.log(f"脚本执行出错: {e}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
        finally:
            self.is_running = False
            self.current_script = None
            self.root.after(0, self.stop_script)

    def on_closing(self):
        """关闭窗口时的处理"""
        if self.is_running:
            self.stop_script()
            time.sleep(0.5)

        # 注销快捷键
        try:
            keyboard.unhook_all()
        except:
            pass

        self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = GameAutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
