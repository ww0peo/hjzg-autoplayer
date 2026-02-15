# 虚拟机自动化方案 - 快速设置指南

## 🎯 方案概述

将你的游戏自动化项目改造为 **主机-虚拟机分离架构**：

- ✅ **虚拟机运行游戏** - 游戏进程与主机隔离
- ✅ **主机运行自动化** - AI 检测和控制逻辑在主机
- ✅ **网络通信** - WebSocket 实时传输截图和输入指令
- ✅ **易于部署** - 最小化改动，保留原有功能

## 📋 前置要求

### 虚拟机（游戏端）
- Windows 系统（推荐 Windows 10/11）
- 至少 4GB RAM
- 网络连接（桥接或 NAT 模式）
- Python 3.8+

### 主机（自动化端）
- Windows 或 Linux
- Python 3.8+
- GPU（可选，加速 YOLO 检测）

## 🚀 5 步快速部署

### 第 1 步：配置虚拟机网络

**虚拟机设置：**
- 网络适配器：**桥接模式**（推荐）
- 或者：NAT 模式 + 端口转发（8765 → 8765）

**获取虚拟机 IP：**
```
Windows: ipconfig
Linux: ip addr show
```

### 第 2 步：虚拟机安装依赖

在虚拟机中运行：
```bash
cd hjzg-autoplayer/vm_proxy
pip install websockets numpy opencv-python pillow pyautogui
```

### 第 3 步：启动虚拟机代理服务器

在虚拟机中运行：
```bash
python remote_server.py
```

看到以下输出表示成功：
```
游戏代理服务器启动中...
监听地址: 0.0.0.0:8765
```

### 第 4 步：主机安装依赖

在主机中运行：
```bash
cd hjzg-autoplayer/vm_proxy
pip install websockets numpy opencv-python pillow
```

### 第 5 步：主机启动 GUI

在主机中运行：
```bash
python remote_gui_script.py
```

## 💡 使用流程

1. **输入虚拟机 IP**
   - 例如：`192.168.1.100`

2. **点击"🔌 连接虚拟机"**
   - 等待状态变为绿色"● 已连接"

3. **点击"🧪 测试连接"**
   - 验证截图和点击是否正常

4. **选择脚本**
   - 例如：`副本刷图`

5. **点击"▶ 启动"**
   - 开始自动化流程

## 📦 文件清单

```
vm_proxy/
├── remote_server.py          # 虚拟机代理服务器
├── remote_client.py          # 主机网络客户端
├── remote_screen_detector.py # 远程屏幕检测器
├── remote_game_input.py      # 远程游戏输入
├── remote_gui_script.py      # 主机 GUI 控制台
├── start_vm_server.bat       # 虚拟机启动脚本
├── start_host_client.bat     # 主机启动脚本
├── config.json               # 配置文件
├── README.md                 # 详细文档
└── SETUP_GUIDE.md            # 本文件
```

## 🔧 常见问题

### Q1: 无法连接虚拟机？

**检查清单：**
- [ ] 虚拟机代理服务器是否在运行？
- [ ] IP 地址是否正确？
- [ ] 防火墙是否允许端口 8765？
- [ ] 虚拟机和主机是否在同一网络？

**测试命令：**
```bash
# 在主机上测试
telnet <虚拟机IP> 8765
```

### Q2: 截图延迟高？

**解决方案：**
1. 降低截图质量（默认 85 → 70）
2. 使用有线网络
3. 升级虚拟机网络适配器（VirtIO/VMXNET3）

### Q3: 点击位置偏移？

**原因：** 分辨率不匹配

**解决：**
1. 固定虚拟机分辨率（1920x1080）
2. 确保游戏窗口全屏

### Q4: 游戏检测不到对象？

**检查：**
- [ ] 模型文件是否存在？（`hjzgv1.pt`）
- [ ] 截图是否正常？
- [ ] 置信度阈值是否过高？

## 📊 性能优化建议

### 网络优化
- 使用 1Gbps 有线网络
- 减少网络跳数（路由器数量）
- 使用 QoS 优先级设置

### 虚拟机优化
- 分配 4GB+ 内存
- 使用 SSD 存储
- 启用 3D 加速

### 主机优化
- 使用 GPU 加速 YOLO 检测
- 关闭不必要的后台程序
- 调整截图质量

## 🔒 安全建议

1. **隔离网络**
   - 使用虚拟机的"仅主机模式"或内部网络
   - 避免暴露代理服务器到公网

2. **防火墙规则**
   ```bash
   # 仅允许主机 IP 访问
   sudo ufw allow from <主机IP> to any port 8765
   ```

3. **定期更新**
   - 更新 Python 依赖
   - 更新虚拟机操作系统

## 🎯 进阶功能

### 多虚拟机控制

创建多个客户端实例：
```python
client1 = RemoteGameClient("192.168.1.100", 8765)
client2 = RemoteGameClient("192.168.1.101", 8765)
```

### 自定义脚本

在 `scripts/` 目录下创建新脚本，继承 `BaseScript`：
```python
from scripts.base_script import BaseScript

class MyScript(BaseScript):
    def get_name(self):
        return "我的脚本"

    def get_description(self):
        return "自定义脚本描述"

    def execute(self):
        # 你的自动化逻辑
        return True

# 注册脚本
from scripts.base_script import AVAILABLE_SCRIPTS
AVAILABLE_SCRIPTS['my_script'] = MyScript
```

## 📞 获取帮助

- 查看 `README.md` 获取详细文档
- 检查日志输出中的错误信息
- 提交 GitHub Issue

---

**祝使用愉快！** 🦞
