"""
远程游戏自动化脚本 - GUI版本（虚拟机架构）

修改自原版 gui_script.py，使用远程客户端替代本地输入/截图
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import time
from datetime import datetime
import json
import os

# 导入远程模块
from remote_screen_detector import RemoteScreenDetector
from remote_game_input import RemoteGameInput
from scripts.base_script import BaseScript


class RemoteGameAutomationGUI:
    """远程游戏自动化图形界面"""

    def __init__(self, root):
        self.root = root
        self.root.title("远程游戏自动化控制台")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # 状态变量
        self.is_running = False
        self.is_paused = False
        self.script_thread = None
        self.detector = None
        self.game_input = None
        self.current_script = None
        self.run_count = 0

        # 配置变量
        self.vm_host = tk.StringVar(value="192.168.1.100")
        self.vm_port = tk.IntVar(value=8765)
        self.window_title = tk.StringVar(value="Torchlight: Infinite")
        self.model_path = tk.StringVar(value="hjzgv1.pt")
        self.conf_threshold = tk.DoubleVar(value=0.5)

        # 获取所有可用脚本
        available_scripts = BaseScript.get_all_scripts()
        self.selected_script = tk.StringVar(
            value=list(available_scripts.keys())[0] if available_scripts else ""
        )

        # 连接状态
        self.is_connected = False

        # 创建界面
        self.create_widgets()

        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """创建界面组件"""

        # ===== 顶部配置区 =====
        config_frame = ttk.LabelFrame(self.root, text="配置", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        # 虚拟机配置
        ttk.Label(config_frame, text="虚拟机IP:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.vm_host, width=20).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(config_frame, text="端口:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.vm_port, width=10).grid(row=0, column=3, padx=5, pady=2)

        # 连接按钮
        self.connect_btn = ttk.Button(
            config_frame,
            text="🔌 连接虚拟机",
            command=self.connect_to_vm,
            width=15
        )
        self.connect_btn.grid(row=0, column=4, padx=5, pady=2)

        # 游戏配置
        ttk.Label(config_frame, text="模型路径:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.model_path, width=30).grid(row=1, column=1, columnspan=2, padx=5, pady=2)

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
        script_combo.grid(row=3, column=1, columnspan=2, padx=5, pady=2)
        script_combo.bind('<<ComboboxSelected>>', self.on_script_changed)

        # ===== 连接状态指示器 =====
        status_frame = ttk.Frame(self.root, padding=5)
        status_frame.pack(fill=tk.X, padx=10)

        ttk.Label(status_frame, text="连接状态:").pack(side=tk.LEFT, padx=5)

        self.connect_status_label = ttk.Label(
            status_frame,
            text="● 未连接",
            foreground="gray",
            font=("Arial", 10, "bold")
        )
        self.connect_status_label.pack(side=tk.LEFT, padx=5)

        # ===== 控制按钮区 =====
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 启动按钮
        self.start_btn = ttk.Button(
            control_frame,
            text="▶ 启动",
            command=self.start_script,
            width=20,
            state=tk.DISABLED
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        # 暂停按钮
        self.pause_btn = ttk.Button(
            control_frame,
            text="⏸ 暂停",
            command=self.pause_script,
            width=20,
            state=tk.DISABLED
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        # 停止按钮
        self.stop_btn = ttk.Button(
            control_frame,
            text="⏹ 停止",
            command=self.stop_script,
            width=20,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # 测试连接按钮
        ttk.Button(
            control_frame,
            text="🧪 测试连接",
            command=self.test_connection,
            width=15
        ).pack(side=tk.LEFT, padx=5)

        # ===== 运行状态指示器 =====
        run_status_frame = ttk.Frame(self.root, padding=5)
        run_status_frame.pack(fill=tk.X, padx=10)

        ttk.Label(run_status_frame, text="运行状态:").pack(side=tk.LEFT, padx=5)

        self.run_status_label = ttk.Label(
            run_status_frame,
            text="● 未启动",
            foreground="gray",
            font=("Arial", 10, "bold")
        )
        self.run_status_label.pack(side=tk.LEFT, padx=5)

        # 运行次数
        self.run_count_label = ttk.Label(run_status_frame, text="运行次数: 0")
        self.run_count_label.pack(side=tk.RIGHT, padx=5)

        # ===== 日志显示区 =====
        log_frame = ttk.LabelFrame(self.root, text="运行日志", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

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
            text="💡 使用步骤: 1) 输入虚拟机IP → 2) 点击'连接虚拟机' → 3) 选择脚本 → 4) 点击'启动'",
            foreground="gray",
            font=("Arial", 8)
        ).pack()

    def log(self, message, level="INFO"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_message, level)
        self.log_text.see(tk.END)

    def connect_to_vm(self):
        """连接到虚拟机"""
        vm_host = self.vm_host.get()
        vm_port = self.vm_port.get()

        self.log(f"正在连接虚拟机 {vm_host}:{vm_port}...", "INFO")

        try:
            # 初始化检测器和输入控制器
            self.detector = RemoteScreenDetector(
                vm_host=vm_host,
                vm_port=vm_port,
                model_path=self.model_path.get(),
                conf=self.conf_threshold.get()
            )

            self.game_input = RemoteGameInput(
                vm_host=vm_host,
                vm_port=vm_port
            )

            self.is_connected = True
            self.connect_status_label.config(text="● 已连接", foreground="green")
            self.connect_btn.config(text="🔌 断开连接")
            self.start_btn.config(state=tk.NORMAL)

            self.log("虚拟机连接成功！", "SUCCESS")
            self.log(f"模型: {self.model_path.get()}", "INFO")
            self.log(f"置信度阈值: {self.conf_threshold.get()}", "INFO")

        except Exception as e:
            self.is_connected = False
            self.connect_status_label.config(text="● 连接失败", foreground="red")
            self.start_btn.config(state=tk.DISABLED)
            self.log(f"连接失败: {e}", "ERROR")

    def disconnect_from_vm(self):
        """断开虚拟机连接"""
        try:
            if self.detector:
                self.detector.__del__()
            if self.game_input:
                self.game_input.__del__()
        except:
            pass

        self.is_connected = False
        self.connect_status_label.config(text="● 未连接", foreground="gray")
        self.connect_btn.config(text="🔌 连接虚拟机")
        self.start_btn.config(state=tk.DISABLED)

        self.log("已断开虚拟机连接", "INFO")

    def test_connection(self):
        """测试连接"""
        if not self.is_connected:
            self.log("请先连接虚拟机", "WARNING")
            return

        try:
            self.log("正在测试连接...", "INFO")

            # 测试截图
            img = self.detector.capture_screen(quality=85)
            self.log(f"截图测试成功，尺寸: {img.shape}", "SUCCESS")

            # 测试点击屏幕中心
            screen_w, screen_h = self.game_input.get_screen_size()
            self.log(f"点击屏幕中心 ({screen_w//2}, {screen_h//2})...", "INFO")
            self.game_input.click(screen_w // 2, screen_h // 2)
            self.log("点击测试成功", "SUCCESS")

            self.log("连接测试完成！", "SUCCESS")

        except Exception as e:
            self.log(f"连接测试失败: {e}", "ERROR")

    def on_script_changed(self, event=None):
        """脚本选择改变时的回调"""
        script_name = self.selected_script.get()
        available_scripts = BaseScript.get_all_scripts()
        if script_name in available_scripts:
            script_class = available_scripts[script_name]
            temp_instance = script_class(self)
            description = temp_instance.get_description()
            self.log(f"已选择脚本: {script_name} - {description}", "INFO")

    def update_run_status(self, text, color):
        """更新运行状态指示器"""
        self.run_status_label.config(text=f"● {text}", foreground=color)

    def start_script(self):
        """启动脚本"""
        if not self.is_connected:
            self.log("请先连接虚拟机", "WARNING")
            return

        if self.is_running:
            if self.is_paused:
                self.is_paused = False
                self.update_run_status("运行中", "green")
                self.pause_btn.config(text="⏸ 暂停")
                self.log("脚本已恢复", "SUCCESS")
            else:
                self.log("脚本已在运行中", "WARNING")
            return

        self.is_running = True
        self.is_paused = False

        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)

        self.update_run_status("运行中", "green")
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
            self.is_paused = False
            self.update_run_status("运行中", "green")
            self.pause_btn.config(text="⏸ 暂停")
            self.log("脚本已恢复", "SUCCESS")
        else:
            self.is_paused = True
            self.update_run_status("已暂停", "orange")
            self.pause_btn.config(text="▶ 恢复")
            self.log("脚本已暂停", "WARNING")

    def stop_script(self):
        """停止脚本"""
        if not self.is_running:
            self.log("脚本未运行", "WARNING")
            return

        self.is_running = False
        self.is_paused = False

        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="⏸ 暂停")
        self.stop_btn.config(state=tk.DISABLED)

        self.update_run_status("已停止", "red")
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

        # 断开连接
        if self.is_connected:
            self.disconnect_from_vm()

        self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = RemoteGameAutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
