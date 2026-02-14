import cv2
import os
from pathlib import Path


def extract_frames(video_path, output_dir, fps=1, prefix="frame", quality=95):
    """
    从视频中抽帧并保存为图片

    参数:
        video_path: 视频文件路径
        output_dir: 输出目录
        fps: 每秒抽取的帧数，默认1帧/秒
        prefix: 输出文件名前缀，默认"frame"
        quality: JPEG质量(0-100)，默认95

    返回:
        成功抽取的帧数
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"错误: 无法打开视频文件 {video_path}")
        return 0

    # 获取视频信息
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / video_fps

    print(f"视频信息:")
    print(f"  FPS: {video_fps:.2f}")
    print(f"  总帧数: {total_frames}")
    print(f"  时长: {duration:.2f}秒")
    print(f"  抽帧间隔: 每{video_fps/fps:.1f}帧抽取1帧")

    # 计算抽帧间隔
    frame_interval = int(video_fps / fps)
    if frame_interval < 1:
        frame_interval = 1

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 按间隔抽帧
        if frame_count % frame_interval == 0:
            # 生成文件名
            filename = f"{prefix}_{saved_count:06d}.jpg"
            filepath = os.path.join(output_dir, filename)

            # 保存图片
            cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
            saved_count += 1

            if saved_count % 10 == 0:
                print(f"已抽取 {saved_count} 帧...")

        frame_count += 1

    cap.release()
    print(f"\n完成! 共抽取 {saved_count} 帧，保存到: {output_dir}")
    return saved_count


def batch_extract_frames(video_dir, output_base_dir, fps=1, quality=95):
    """
    批量处理目录下的所有视频

    参数:
        video_dir: 视频目录
        output_base_dir: 输出根目录
        fps: 每秒抽取的帧数
        quality: JPEG质量
    """
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv']
    video_dir = Path(video_dir)

    video_files = []
    for ext in video_extensions:
        video_files.extend(video_dir.glob(f"*{ext}"))

    if not video_files:
        print(f"在 {video_dir} 中未找到视频文件")
        return

    print(f"找到 {len(video_files)} 个视频文件\n")

    for i, video_path in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] 处理: {video_path.name}")

        # 为每个视频创建单独的输出目录
        output_dir = os.path.join(output_base_dir, video_path.stem)

        extract_frames(
            str(video_path),
            output_dir,
            fps=fps,
            prefix=video_path.stem,
            quality=quality
        )


if __name__ == "__main__":
    # 示例1: 单个视频抽帧
    extract_frames(
        video_path="test2.mp4",
        output_dir="frames",
        prefix="val_frame",
        fps=1,  # 每秒1帧
        quality=95
    )