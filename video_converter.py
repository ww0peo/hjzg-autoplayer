import cv2
import os
from pathlib import Path
from typing import Optional, Union, Tuple
import subprocess


class VideoConverter:
    """
    视频格式转换类

    功能：
    1. AVI转MP4
    2. 支持多种视频格式转换
    3. 支持批量转换
    4. 可调整分辨率、帧率、编码器
    """

    def __init__(self):
        """初始化转换器"""
        self.supported_formats = ['.avi', '.mp4', '.mov', '.mkv', '.flv', '.wmv', '.webm']

    def avi_to_mp4(self, input_path: str, output_path: Optional[str] = None,
                   codec: str = 'mp4v', fps: Optional[int] = None,
                   resolution: Optional[Tuple[int, int]] = None) -> bool:
        """
        将AVI视频转换为MP4格式

        参数:
            input_path: 输入AVI文件路径
            output_path: 输出MP4文件路径（None则自动生成）
            codec: 视频编码器
                - 'mp4v': MPEG-4编码（兼容性好）
                - 'avc1': H.264编码（推荐，质量好）
                - 'x264': H.264编码（需要额外安装）
            fps: 输出帧率（None保持原帧率）
            resolution: 输出分辨率 (width, height)（None保持原分辨率）

        返回:
            转换是否成功
        """
        # 检查输入文件
        if not os.path.exists(input_path):
            print(f"错误: 文件不存在 - {input_path}")
            return False

        # 生成输出路径
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.with_suffix('.mp4'))

        # 打开输入视频
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"错误: 无法打开视频 - {input_path}")
            return False

        try:
            # 获取视频信息
            original_fps = int(cap.get(cv2.CAP_PROP_FPS))
            original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # 设置输出参数
            output_fps = fps if fps else original_fps
            output_width, output_height = resolution if resolution else (original_width, original_height)

            print(f"输入视频: {input_path}")
            print(f"  分辨率: {original_width}x{original_height}")
            print(f"  帧率: {original_fps} fps")
            print(f"  总帧数: {total_frames}")
            print(f"\n输出视频: {output_path}")
            print(f"  分辨率: {output_width}x{output_height}")
            print(f"  帧率: {output_fps} fps")
            print(f"  编码器: {codec}")

            # 创建视频写入器
            fourcc = cv2.VideoWriter_fourcc(*codec)
            out = cv2.VideoWriter(output_path, fourcc, output_fps, (output_width, output_height))

            if not out.isOpened():
                print(f"错误: 无法创建输出视频")
                return False

            # 逐帧转换
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # 调整分辨率（如果需要）
                if resolution:
                    frame = cv2.resize(frame, (output_width, output_height))

                out.write(frame)
                frame_count += 1

                # 显示进度
                if frame_count % 100 == 0:
                    progress = (frame_count / total_frames) * 100
                    print(f"进度: {frame_count}/{total_frames} ({progress:.1f}%)")

            print(f"\n转换完成! 共处理 {frame_count} 帧")
            print(f"输出文件: {output_path}")
            return True

        except Exception as e:
            print(f"转换失败: {e}")
            return False

        finally:
            cap.release()
            if 'out' in locals():
                out.release()

    def convert_video(self, input_path: str, output_path: Optional[str] = None,
                     output_format: str = 'mp4', codec: Optional[str] = None,
                     fps: Optional[int] = None, resolution: Optional[Tuple[int, int]] = None) -> bool:
        """
        通用视频格式转换

        参数:
            input_path: 输入视频路径
            output_path: 输出视频路径
            output_format: 输出格式（mp4, avi, mov等）
            codec: 视频编码器（None则自动选择）
            fps: 输出帧率
            resolution: 输出分辨率

        返回:
            转换是否成功
        """
        # 检查输入文件
        if not os.path.exists(input_path):
            print(f"错误: 文件不存在 - {input_path}")
            return False

        # 生成输出路径
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.with_suffix(f'.{output_format}'))

        # 自动选择编码器
        if codec is None:
            codec_map = {
                'mp4': 'mp4v',
                'avi': 'XVID',
                'mov': 'mp4v',
                'mkv': 'X264',
            }
            codec = codec_map.get(output_format, 'mp4v')

        # 打开输入视频
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"错误: 无法打开视频 - {input_path}")
            return False

        try:
            # 获取视频信息
            original_fps = int(cap.get(cv2.CAP_PROP_FPS))
            original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # 设置输出参数
            output_fps = fps if fps else original_fps
            output_width, output_height = resolution if resolution else (original_width, original_height)

            print(f"转换: {Path(input_path).name} -> {Path(output_path).name}")
            print(f"编码器: {codec}, 帧率: {output_fps} fps")

            # 创建视频写入器
            fourcc = cv2.VideoWriter_fourcc(*codec)
            out = cv2.VideoWriter(output_path, fourcc, output_fps, (output_width, output_height))

            if not out.isOpened():
                print(f"错误: 无法创建输出视频")
                return False

            # 逐帧转换
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if resolution:
                    frame = cv2.resize(frame, (output_width, output_height))

                out.write(frame)
                frame_count += 1

                if frame_count % 100 == 0:
                    progress = (frame_count / total_frames) * 100
                    print(f"进度: {progress:.1f}%", end='\r')

            print(f"\n转换完成! 输出: {output_path}")
            return True

        except Exception as e:
            print(f"转换失败: {e}")
            return False

        finally:
            cap.release()
            if 'out' in locals():
                out.release()

    def batch_convert(self, input_dir: str, output_dir: Optional[str] = None,
                     input_format: str = 'avi', output_format: str = 'mp4') -> int:
        """
        批量转换视频格式

        参数:
            input_dir: 输入目录
            output_dir: 输出目录（None则使用输入目录）
            input_format: 输入格式
            output_format: 输出格式

        返回:
            成功转换的文件数量
        """
        if not os.path.exists(input_dir):
            print(f"错误: 目录不存在 - {input_dir}")
            return 0

        # 设置输出目录
        if output_dir is None:
            output_dir = input_dir
        else:
            os.makedirs(output_dir, exist_ok=True)

        # 查找所有匹配的文件
        input_files = list(Path(input_dir).glob(f'*.{input_format}'))

        if not input_files:
            print(f"未找到 .{input_format} 文件")
            return 0

        print(f"找到 {len(input_files)} 个 .{input_format} 文件")
        print(f"开始批量转换...\n")

        success_count = 0
        for i, input_file in enumerate(input_files, 1):
            print(f"\n[{i}/{len(input_files)}] 处理: {input_file.name}")

            output_file = Path(output_dir) / input_file.with_suffix(f'.{output_format}').name

            if self.convert_video(str(input_file), str(output_file), output_format):
                success_count += 1

        print(f"\n批量转换完成!")
        print(f"成功: {success_count}/{len(input_files)}")
        return success_count

    def convert_with_ffmpeg(self, input_path: str, output_path: Optional[str] = None,
                           codec: str = 'libx264', crf: int = 23) -> bool:
        """
        使用FFmpeg转换（需要安装FFmpeg）

        参数:
            input_path: 输入视频路径
            output_path: 输出视频路径
            codec: 视频编码器（libx264, libx265等）
            crf: 质量参数（0-51，越小质量越好，推荐18-28）

        返回:
            转换是否成功
        """
        try:
            # 检查FFmpeg是否安装
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("错误: 未安装FFmpeg")
            print("请访问 https://ffmpeg.org/download.html 下载安装")
            return False

        # 生成输出路径
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.with_suffix('.mp4'))

        # 构建FFmpeg命令
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', codec,
            '-crf', str(crf),
            '-c:a', 'aac',
            '-y',  # 覆盖输出文件
            output_path
        ]

        print(f"使用FFmpeg转换: {input_path} -> {output_path}")
        print(f"编码器: {codec}, CRF: {crf}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"转换完成: {output_path}")
                return True
            else:
                print(f"转换失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"错误: {e}")
            return False


# 使用示例
if __name__ == "__main__":
    converter = VideoConverter()

    # 示例1: 简单的AVI转MP4
    print("=== 示例1: AVI转MP4 ===")
    converter.avi_to_mp4(r'runs\detect\runs\detect\predict\test2.avi', 'output.mp4')

    # # 示例2: 转换并调整分辨率和帧率
    # print("\n=== 示例2: 转换并调整参数 ===")
    # converter.avi_to_mp4(
    #     input_path='input.avi',
    #     output_path='output_720p.mp4',
    #     codec='mp4v',
    #     fps=30,
    #     resolution=(1280, 720)
    # )

    # # 示例3: 通用格式转换
    # print("\n=== 示例3: 通用格式转换 ===")
    # converter.convert_video(
    #     input_path='input.avi',
    #     output_format='mp4',
    #     codec='mp4v'
    # )

    # # 示例4: 批量转换
    # print("\n=== 示例4: 批量转换 ===")
    # converter.batch_convert(
    #     input_dir='videos/',
    #     output_dir='converted/',
    #     input_format='avi',
    #     output_format='mp4'
    # )

    # # 示例5: 使用FFmpeg转换（高质量）
    # print("\n=== 示例5: FFmpeg转换 ===")
    # converter.convert_with_ffmpeg(
    #     input_path=r'runs\detect\runs\detect\predict\test2.avi',
    #     output_path='output_hq.mp4',
    #     codec='libx264',
    #     crf=18  # 高质量
    # )
