from ultralytics import YOLO
import torch
import gc


def train_yolo_model(data_yaml, model_name='yolov8n.pt', epochs=100, imgsz=640,
                     batch=16, workers=4, device=0, save_period=10):
    """
    训练YOLO模型（优化内存使用）

    参数:
        data_yaml: 数据集配置文件路径
        model_name: 预训练模型名称
        epochs: 训练轮数
        imgsz: 输入图片尺寸
        batch: 批次大小（减小可降低内存使用）
        workers: 数据加载线程数
        device: GPU设备ID，0表示第一块GPU
        save_period: 每N个epoch保存一次模型（-1表示只保存最后和最佳）
    """
    # 清理GPU缓存
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()
        print(f"使用GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU内存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

    # 加载预训练模型
    model = YOLO(model_name)

    # 训练模型（优化参数）
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,              # 批次大小，内存不足时减小
        workers=workers,          # 数据加载线程数
        device=device,            # GPU设备
        save=True,                # 保存检查点
        save_period=save_period,  # 保存间隔（减少保存频率）
        cache=False,              # 不缓存图片到内存（节省内存）
        amp=True,                 # 自动混合精度训练（节省内存）
        patience=50,              # 早停耐心值
        project='runs/train',     # 项目目录
        name='game_detection',    # 实验名称
        exist_ok=True,            # 允许覆盖
        pretrained=True,          # 使用预训练权重
        optimizer='AdamW',        # 优化器
        verbose=True,             # 详细输出
        seed=42,                  # 随机种子
        deterministic=False,      # 不使用确定性算法（更快）
        single_cls=False,         # 多类别检测
        rect=False,               # 矩形训练
        cos_lr=True,              # 余弦学习率调度
        close_mosaic=10,          # 最后N个epoch关闭mosaic增强
        resume=False,             # 是否恢复训练
        fraction=1.0,             # 使用数据集的比例
    )

    # 训练完成后清理内存
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()

    print("\n训练完成!")
    print(f"最佳模型保存在: runs/train/game_detection/weights/best.pt")
    print(f"最后模型保存在: runs/train/game_detection/weights/last.pt")

    return results


def resume_training(checkpoint_path, data_yaml, epochs=100):
    """
    从检查点恢复训练

    参数:
        checkpoint_path: 检查点路径，例如 'runs/train/game_detection/weights/last.pt'
        data_yaml: 数据集配置文件
        epochs: 继续训练的轮数
    """
    model = YOLO(checkpoint_path)
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        resume=True
    )
    return results


if __name__ == "__main__":
    # 定义数据集配置文件路径
    data_yaml = 'yolo_dataset.yaml'

    # 根据你的需求选择模型：
    # 'yolov8n.pt' - 最快，适合实时检测和小数据集（推荐）
    # 'yolov8s.pt' - 平衡速度和精度
    # 'yolov8m.pt' - 更高精度，需要更多GPU内存（4-6GB）
    # 'yolov8l.pt' - 高精度，需要8GB+显存
    # 'yolov8x.pt' - 最高精度，需要12GB+显存

    # 训练模型（优化参数以避免内存错误）
    train_yolo_model(
        data_yaml=data_yaml,
        model_name='yolov8n.pt',  # 根据GPU内存和需求选择
        epochs=300,
        imgsz=640,
        batch=8,                  # 内存不足时改为4或2
        workers=2,                # 减少工作线程
        device=0,                 # 使用第一块GPU
        save_period=20            # 每20个epoch保存一次
    )

    # 如果训练中断，可以使用以下代码恢复训练
    # resume_training(
    #     checkpoint_path=r'runs\detect\train\weights\last.pt',
    #     data_yaml=data_yaml,
    #     epochs=300
    # )