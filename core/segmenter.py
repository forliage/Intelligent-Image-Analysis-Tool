import cv2
import numpy as np
import torch
import torchvision.models as models
from PIL import Image

# --- 模型懒加载 ---
segmentation_model = None
preprocess_transform = None

PALETTE = [[0, 0, 0], [128, 0, 0], [0, 128, 0], [128, 128, 0], [0, 0, 128],
           [128, 0, 128], [0, 128, 128], [128, 128, 128], [64, 0, 0],
           [192, 0, 0], [64, 128, 0], [192, 128, 0], [64, 0, 128],
           [192, 0, 128], [64, 128, 128], [192, 128, 128], [0, 64, 0],
           [128, 64, 0], [0, 192, 0], [128, 192, 0], [0, 64, 128]]

def initialize_segmentation_model():
    """
    初始化DeepLabV3模型。如果已初始化，则直接返回。
    """
    global segmentation_model, preprocess_transform
    if segmentation_model is None:
        print("Initializing DeepLabV3 model for the first time...")
        weights = models.segmentation.DeepLabV3_ResNet101_Weights.DEFAULT
        segmentation_model = models.segmentation.deeplabv3_resnet101(weights=weights)
        segmentation_model.eval()
        preprocess_transform = weights.transforms()
        print("DeepLabV3 model initialized.")

def segment_image_deep(cv_image: np.ndarray) -> np.ndarray:
    """
    使用DeepLabV3对图像进行语义分割。
    """
    # 确保模型已初始化
    initialize_segmentation_model()

    rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    input_tensor = preprocess_transform(pil_image)
    input_batch = input_tensor.unsqueeze(0)
    
    with torch.no_grad():
        output = segmentation_model(input_batch)['out'][0]
    
    output_predictions = output.argmax(0)
    return output_predictions.byte().cpu().numpy()

def draw_segmentation_mask(original_cv_image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    将分割掩码以彩色形式叠加到原始图像上。
    """
    color_mask = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
    for class_id, color in enumerate(PALETTE):
        color_mask[mask == class_id] = color
    
    # --- 【关键修复】 ---
    # 在混合前，将彩色掩码缩放到与原始图像完全相同的尺寸
    target_h, target_w = original_cv_image.shape[:2]
    # 使用INTER_NEAREST（最近邻插值）来缩放掩码，避免产生模糊的边界颜色
    resized_color_mask = cv2.resize(color_mask, (target_w, target_h), interpolation=cv2.INTER_NEAREST)

    alpha = 0.6
    beta = 1.0 - alpha
    # 使用缩放后的掩码进行混合
    blended_image = cv2.addWeighted(original_cv_image, alpha, resized_color_mask, beta, 0)
    
    return blended_image