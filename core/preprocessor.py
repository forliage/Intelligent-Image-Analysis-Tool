import cv2
import numpy as np
import config

def preprocess_image(image_path: str) -> np.ndarray | None:
    """
    加载图像，并将其预处理到固定尺寸。

    Args:
        image_path (str): 输入图像的文件路径。

    Returns:
        np.ndarray | None: 返回一个经过缩放的OpenCV图像（NumPy数组，BGR格式），
                           如果读取失败则返回 None。
    """
    # 使用OpenCV读取图像
    image = cv2.imread(image_path)

    if image is None:
        print(f"错误：无法从路径读取图像: {image_path}")
        return None

    # 获取配置中定义的目标尺寸
    target_size = (config.FIXED_IMAGE_WIDTH, config.FIXED_IMAGE_HEIGHT)

    # 调整图像大小
    # cv2.INTER_AREA 插值方法通常在缩小图像时能得到最好的效果
    resized_image = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

    return resized_image