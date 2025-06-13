import cv2
import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

import config

# --- 模型懒加载 ---
# 将模型变量初始化为None，避免在导入时加载
resnet_model = None
feature_extractor_model = None
preprocess_transform = None

def initialize_resnet_model():
    """
    初始化ResNet模型。如果已初始化，则直接返回。
    """
    global resnet_model, feature_extractor_model, preprocess_transform
    if resnet_model is None:
        print("Initializing ResNet-50 model for the first time...")
        weights = models.ResNet50_Weights.IMAGENET1K_V2
        resnet_model = models.resnet50(weights=weights)
        resnet_model.eval()
        feature_extractor_model = torch.nn.Sequential(*list(resnet_model.children())[:-1])
        preprocess_transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        print("ResNet-50 model initialized.")

# --- 特征提取函数 ---
def extract_color_histogram(cv_image: np.ndarray) -> (np.ndarray, str):
    # ... (此函数内容不变) ...
    channels = cv2.split(cv_image)
    histograms = []
    for chan in channels:
        hist = cv2.calcHist([chan], [0], None, [config.HIST_BINS], [0, 256])
        cv2.normalize(hist, hist)
        histograms.append(hist)
    feature_vector = np.concatenate(histograms).flatten()
    description = (
        f"--- 颜色直方图特征 ---\n"
        f"类型: BGR三通道拼接\n"
        f"每个通道的Bin数量: {config.HIST_BINS}\n"
        f"特征向量维度 (Shape): {feature_vector.shape}\n"
        f"向量范数 (Norm): {np.linalg.norm(feature_vector):.4f}"
    )
    return feature_vector, description


def extract_deep_features(cv_image: np.ndarray) -> (torch.Tensor, str):
    """
    使用预训练的ResNet-50模型提取深度特征。
    """
    # 在函数开始时确保模型已初始化
    initialize_resnet_model()

    rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    input_tensor = preprocess_transform(pil_image)
    input_batch = input_tensor.unsqueeze(0)
    
    with torch.no_grad():
        features = feature_extractor_model(input_batch)
    
    feature_vector = features.flatten()
    
    description = (
        f"\n--- 深度学习特征 (ResNet-50) ---\n"
        f"模型: ResNet-50 (IMAGENET1K_V2 weights)\n"
        f"特征来源: 全局平均池化层之后\n"
        f"特征向量维度 (Shape): {feature_vector.shape}\n"
        f"向量范数 (Norm): {torch.linalg.norm(feature_vector):.4f}"
    )
    return feature_vector, description