from ultralytics import YOLO
import cv2
import torch
import gc
from pathlib import Path


def predict_video(model_path, video_path, output_dir='runs/detect',
                  conf=0.25, iou=0.7, imgsz=640, show=False, save=True,
                  max_det=300, stream_buffer=1):
    """
    视频目标检测（优化内存使用）

    参数:
        model_path: 模型路径
        video_path: 视频路径
        output_dir: 输出目录
        conf: 置信度阈值
        iou: NMS的IoU阈值
        imgsz: 推理图片尺寸（减小可降低内存）
        show: 是否实时显示（会占用更多内存）
        save: 是否保存结果视频
        max_det: 每帧最大检测数
        stream_buffer: 流缓冲区大小（减小可降低内存）
    """
    # 清理内存
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()

    # 加载模型
    model = YOLO(model_path)

    print(f"开始处理视频: {video_path}")
    print(f"推理尺寸: {imgsz}x{imgsz}")
    print(f"置信度阈值: {conf}")

    try:
        # 使用stream模式逐帧处理（节省内存）
        results = model.predict(
            source=video_path,
            conf=conf,
            iou=iou,
            imgsz=imgsz,
            show=show,
            save=save,
            project=output_dir,
            name='predict',
            exist_ok=True,
            stream=True,           # 流式处理，节省内存
            verbose=False,         # 减少输出
            max_det=max_det,
            vid_stride=1,          # 视频帧间隔（增大可跳帧，加快速度）
            device=0,              # GPU设备
        )

        # 逐帧处理
        frame_count = 0
        for result in results:
            frame_count += 1
            if frame_count % 100 == 0:
                print(f"已处理 {frame_count} 帧")
                # 定期清理内存
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

        print(f"\n处理完成! 共处理 {frame_count} 帧")
        print(f"结果保存在: {output_dir}/predict")

    except Exception as e:
        print(f"错误: {e}")
        print("\n建议:")
        print("1. 减小 imgsz 参数 (例如: 416 或 320)")
        print("2. 关闭 show=False")
        print("3. 增大 vid_stride 跳帧处理")
        print("4. 使用 predict_video_manual() 手动控制内存")

    finally:
        # 清理内存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()


def predict_video_manual(model_path, video_path, output_path='output.mp4',
                        conf=0.25, imgsz=640, skip_frames=1):
    """
    手动逐帧处理视频（最大程度控制内存）

    参数:
        model_path: 模型路径
        video_path: 输入视频路径
        output_path: 输出视频路径
        conf: 置信度阈值
        imgsz: 推理尺寸
        skip_frames: 跳帧数（1=处理每帧，2=处理每2帧）
    """
    # 加载模型
    model = YOLO(model_path)

    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"错误: 无法打开视频 {video_path}")
        return

    # 获取视频信息
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"视频信息: {width}x{height} @ {fps}fps, 共{total_frames}帧")

    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0
    processed_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # 跳帧处理
            if frame_count % skip_frames != 0:
                out.write(frame)
                continue

            # 推理
            results = model.predict(
                source=frame,
                conf=conf,
                imgsz=imgsz,
                verbose=False,
                device=0
            )

            # 绘制结果
            annotated_frame = results[0].plot()
            out.write(annotated_frame)

            processed_count += 1

            # 显示进度
            if frame_count % 100 == 0:
                print(f"进度: {frame_count}/{total_frames} ({frame_count/total_frames*100:.1f}%)")
                # 清理内存
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                gc.collect()

        print(f"\n处理完成!")
        print(f"总帧数: {frame_count}, 处理帧数: {processed_count}")
        print(f"输出视频: {output_path}")

    finally:
        cap.release()
        out.release()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()


def predict_image(model_path, image_path, conf=0.25, save=True):
    """
    单张图片预测

    参数:
        model_path: 模型路径
        image_path: 图片路径或目录
        conf: 置信度阈值
        save: 是否保存结果
    """
    model = YOLO(model_path)

    results = model.predict(
        source=image_path,
        conf=conf,
        save=save,
        project='runs/detect',
        name='predict_images',
        exist_ok=True
    )

    print(f"检测完成! 结果保存在: runs/detect/predict_images")
    return results


def predict_realtime_camera(model_path, conf=0.25, camera_id=0):
    """
    实时摄像头检测

    参数:
        model_path: 模型路径
        conf: 置信度阈值
        camera_id: 摄像头ID（0为默认摄像头）
    """
    model = YOLO(model_path)

    cap = cv2.VideoCapture(camera_id)

    print("按 'q' 退出")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 推理
            results = model.predict(source=frame, conf=conf, verbose=False)

            # 显示结果
            annotated_frame = results[0].plot()
            cv2.imshow('YOLO Detection', annotated_frame)

            # 按q退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    model_path = "hjzgv1.pt"
    video_path = "test2.mp4"

    # 方案1: 优化的视频推理（推荐）
    print("=== 方案1: 优化视频推理 ===")
    predict_video(
        model_path=model_path,
        video_path=video_path,
        conf=0.25,
        imgsz=416,          # 减小尺寸降低内存（原640）
        show=False,         # 关闭实时显示节省内存
        save=True,
        stream_buffer=1
    )

    # 方案2: 手动控制内存（内存极度不足时使用）
    # print("\n=== 方案2: 手动逐帧处理 ===")
    # predict_video_manual(
    #     model_path=model_path,
    #     video_path=video_path,
    #     output_path='output_manual.mp4',
    #     conf=0.25,
    #     imgsz=416,
    #     skip_frames=2      # 每2帧处理1帧（加快速度）
    # )

    # 方案3: 图片预测
    # predict_image(
    #     model_path=model_path,
    #     image_path='test_images/',  # 图片路径或目录
    #     conf=0.25
    # )

    # 方案4: 实时摄像头检测
    # predict_realtime_camera(
    #     model_path=model_path,
    #     conf=0.25,
    #     camera_id=0
    # )
