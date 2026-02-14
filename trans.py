import xml.etree.ElementTree as ET
import os
from pathlib import Path
import shutil


def convert_voc_to_yolo(voc_xml_path, yolo_txt_path, class_names):
    """
    将单个VOC XML文件转换为YOLO格式

    参数:
        voc_xml_path: VOC XML文件路径
        yolo_txt_path: 输出的YOLO txt文件路径
        class_names: 类别名称列表，例如 ['person', 'car', 'dog']

    YOLO格式: <class_id> <x_center> <y_center> <width> <height>
    所有坐标都是相对于图片尺寸的归一化值(0-1)
    """
    try:
        tree = ET.parse(voc_xml_path)
        root = tree.getroot()

        # 获取图片尺寸
        size = root.find('size')
        img_width = int(size.find('width').text)
        img_height = int(size.find('height').text)

        yolo_annotations = []

        # 遍历所有目标对象
        for obj in root.findall('object'):
            class_name = obj.find('name').text

            # 检查类别是否在类别列表中
            if class_name not in class_names:
                print(f"警告: 类别 '{class_name}' 不在类别列表中，跳过")
                continue

            class_id = class_names.index(class_name)

            # 获取边界框坐标
            bbox = obj.find('bndbox')
            xmin = float(bbox.find('xmin').text)
            ymin = float(bbox.find('ymin').text)
            xmax = float(bbox.find('xmax').text)
            ymax = float(bbox.find('ymax').text)

            # 转换为YOLO格式 (归一化的中心点坐标和宽高)
            x_center = ((xmin + xmax) / 2) / img_width
            y_center = ((ymin + ymax) / 2) / img_height
            width = (xmax - xmin) / img_width
            height = (ymax - ymin) / img_height

            # 确保值在0-1范围内
            x_center = max(0, min(1, x_center))
            y_center = max(0, min(1, y_center))
            width = max(0, min(1, width))
            height = max(0, min(1, height))

            # YOLO格式: class_id x_center y_center width height
            yolo_annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

        # 写入YOLO格式文件
        with open(yolo_txt_path, 'w') as f:
            f.write('\n'.join(yolo_annotations))

        return len(yolo_annotations)

    except Exception as e:
        print(f"错误: 处理 {voc_xml_path} 时出错: {e}")
        return 0


def batch_convert_voc_to_yolo(voc_dir, output_dir, class_names, copy_images=True):
    """
    批量转换VOC格式数据集到YOLO格式

    目录结构:
    voc_dir/
        ├── Annotations/  (XML文件)
        └── JPEGImages/   (图片文件)

    输出结构:
    output_dir/
        ├── images/       (图片)
        ├── labels/       (YOLO txt文件)
        └── classes.txt   (类别列表)

    参数:
        voc_dir: VOC数据集根目录
        output_dir: 输出目录
        class_names: 类别名称列表
        copy_images: 是否复制图片文件
    """
    voc_dir = Path(voc_dir)
    output_dir = Path(output_dir)

    # 创建输出目录
    images_dir = output_dir / 'images'
    labels_dir = output_dir / 'labels'
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    # 保存类别列表
    classes_file = output_dir / 'classes.txt'
    with open(classes_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(class_names))
    print(f"类别列表已保存到: {classes_file}")

    # 获取所有XML文件
    annotations_dir = voc_dir / 'Annotations'
    images_source_dir = voc_dir / 'JPEGImages'

    if not annotations_dir.exists():
        print(f"错误: 找不到 {annotations_dir}")
        return

    xml_files = list(annotations_dir.glob('*.xml'))
    if not xml_files:
        print(f"错误: 在 {annotations_dir} 中未找到XML文件")
        return

    print(f"\n找到 {len(xml_files)} 个XML文件")
    print(f"类别列表: {class_names}\n")

    success_count = 0
    total_objects = 0

    for i, xml_file in enumerate(xml_files, 1):
        # 生成对应的txt文件名
        txt_file = labels_dir / f"{xml_file.stem}.txt"

        # 转换
        obj_count = convert_voc_to_yolo(str(xml_file), str(txt_file), class_names)

        if obj_count > 0:
            success_count += 1
            total_objects += obj_count

            # 复制对应的图片
            if copy_images:
                # 尝试多种图片格式
                for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
                    img_source = images_source_dir / f"{xml_file.stem}{ext}"
                    if img_source.exists():
                        img_dest = images_dir / img_source.name
                        shutil.copy2(img_source, img_dest)
                        break

        if i % 100 == 0:
            print(f"已处理 {i}/{len(xml_files)} 个文件...")

    print(f"\n转换完成!")
    print(f"成功转换: {success_count}/{len(xml_files)} 个文件")
    print(f"总目标数: {total_objects}")
    print(f"输出目录: {output_dir}")


def create_yolo_dataset_yaml(output_dir, class_names, train_ratio=0.8):
    """
    创建YOLO训练所需的dataset.yaml配置文件

    参数:
        output_dir: 数据集目录
        class_names: 类别名称列表
        train_ratio: 训练集比例
    """
    output_dir = Path(output_dir)
    yaml_content = f"""# YOLO Dataset Configuration
path: {output_dir.absolute()}  # 数据集根目录
train: images  # 训练集图片目录
val: images    # 验证集图片目录

# 类别数量
nc: {len(class_names)}

# 类别名称
names: {class_names}
"""

    yaml_file = output_dir / 'dataset.yaml'
    with open(yaml_file, 'w', encoding='utf-8') as f:
        f.write(yaml_content)

    print(f"\nYOLO配置文件已创建: {yaml_file}")


def split_dataset(images_dir, labels_dir, output_dir, train_ratio=0.8, val_ratio=0.1):
    """
    将数据集划分为训练集、验证集和测试集

    参数:
        images_dir: 图片目录
        labels_dir: 标签目录
        output_dir: 输出目录
        train_ratio: 训练集比例
        val_ratio: 验证集比例
    """
    import random

    images_dir = Path(images_dir)
    labels_dir = Path(labels_dir)
    output_dir = Path(output_dir)

    # 获取所有图片文件
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png']:
        image_files.extend(images_dir.glob(f'*{ext}'))

    if not image_files:
        print("错误: 未找到图片文件")
        return

    # 打乱顺序
    random.shuffle(image_files)

    # 计算划分数量
    total = len(image_files)
    train_count = int(total * train_ratio)
    val_count = int(total * val_ratio)

    train_files = image_files[:train_count]
    val_files = image_files[train_count:train_count + val_count]
    test_files = image_files[train_count + val_count:]

    # 创建目录结构
    for split in ['train', 'val', 'test']:
        (output_dir / split / 'images').mkdir(parents=True, exist_ok=True)
        (output_dir / split / 'labels').mkdir(parents=True, exist_ok=True)

    # 复制文件
    def copy_split(files, split_name):
        for img_file in files:
            # 复制图片
            shutil.copy2(img_file, output_dir / split_name / 'images' / img_file.name)

            # 复制标签
            label_file = labels_dir / f"{img_file.stem}.txt"
            if label_file.exists():
                shutil.copy2(label_file, output_dir / split_name / 'labels' / label_file.name)

    print(f"\n划分数据集:")
    print(f"训练集: {len(train_files)} ({train_ratio*100:.0f}%)")
    print(f"验证集: {len(val_files)} ({val_ratio*100:.0f}%)")
    print(f"测试集: {len(test_files)} ({(1-train_ratio-val_ratio)*100:.0f}%)")

    copy_split(train_files, 'train')
    copy_split(val_files, 'val')
    copy_split(test_files, 'test')

    print(f"\n数据集已划分到: {output_dir}")


if __name__ == "__main__":
    # 示例1: 批量转换VOC到YOLO
    class_names = ['person', 'portal1', 'portal2', 'button1', 'button2', 'dungeon', 'startButton', 'boss', 'monster', 'props']  # 根据你的游戏修改

    batch_convert_voc_to_yolo(
        voc_dir='test',  # VOC数据集目录
        output_dir='bak',     # 输出目录
        class_names=class_names,
        copy_images=True
    )

    # # 示例2: 创建YOLO配置文件
    # create_yolo_dataset_yaml(
    #     output_dir='yolo_dataset',
    #     class_names=class_names
    # )

    # 示例3: 划分数据集（可选）
    # split_dataset(
    #     images_dir='yolo_dataset/images',
    #     labels_dir='yolo_dataset/labels',
    #     output_dir='yolo_dataset_split',
    #     train_ratio=0.8,
    #     val_ratio=0.1
    # )
