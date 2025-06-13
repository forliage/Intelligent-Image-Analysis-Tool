# 智能图像分析工具 (Intelligent Image Analysis Tool)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-1.10+-ee4c2c.svg)](https://pytorch.org/)
[![PyQt6](https://img.shields.io/badge/PyQt-6-4A90E2.svg)](https://riverbankcomputing.com/software/pyqt/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-5C3EE8.svg)](https://opencv.org/)

这是一个专为计算机视觉研究人员设计的桌面应用程序。它提供了一个自动化的图像处理流水线，能够对用户输入的图片进行预处理、特征提取和目标分割，并以可视化的方式展示结果。

## ✨ 主要功能 (Features)

1.  **图像预处理**:
    *   支持多种常见图像格式输入 (`.jpg`, `.png`, `.bmp` 等)。
    *   自动将图像缩放到统一的固定尺寸。
    *   将所有处理后的图像统一为 `.png` 无损格式。

2.  **多样化特征提取**:
    *   **经典特征**: 计算并展示图像的颜色直方图。
    *   **深度特征**: 使用预训练的PyTorch模型 (如 ResNet-50) 提取高维语义特征向量。

3.  **主体与部件分割**:
    *   **轮廓检测**: 快速标记图像中的主要物体轮廓。
    *   **深度学习分割**: 使用预训练的语义分割模型 (如 DeepLabV3) 对图像进行像素级分割，识别不同对象。

4.  **可视化展示**:
    *   并排显示原始图像、预处理后图像和分割结果图。
    *   清晰地展示提取出的特征向量（或其摘要信息）。

5.  **友好用户界面**:
    *   基于 PyQt6 构建，提供简洁直观的图形用户界面。

## 🛠️ 技术栈 (Technology Stack)

*   **GUI**: PyQt6
*   **深度学习**: PyTorch
*   **核心图像处理**: OpenCV-Python
*   **数值计算**: NumPy
*   **绘图**: Matplotlib (用于绘制直方图等)

## 📂 项目结构 (Project Structure)

```
intelligent_image_analyzer/
│
├── main.py                 # 项目主入口
├── requirements.txt        # 项目依赖库
├── config.py               # 配置文件
├── README.md               # 项目说明文档
│
├── core/                   # 核心处理逻辑模块
│   ├── preprocessor.py
│   ├── feature_extractor.py
│   └── segmenter.py
│
├── gui/                    # PyQt6 GUI相关代码
│   └── main_window.py
│
├── assets/                 # 资源文件 (如图标)
│
└── sample_images/          # 示例图片
```

## 🚀 安装与运行 (Installation & Usage)

1.  **克隆仓库**
    ```bash
    git clone https://github.com/forliage/Intelligent-Image-Analysis-Tool.git
    cd intelligent_image_analyzer
    ```

2.  **创建并激活Python虚拟环境 (推荐)**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```
    *注意: PyTorch模型将在首次运行时自动下载并缓存到本地。请确保网络连接通畅。*

4.  **运行程序**
    ```bash
    python main.py
    ```

## 📖 如何使用 (How to Use)

1.  启动应用程序后，点击 **"打开图片"** 按钮。
2.  在文件对话框中选择一张图片。
3.  程序将自动执行所有处理步骤。
4.  处理结果将显示在界面的相应区域：
    *   左侧为原始图片和预处理后的图片。
    *   右侧为分割标注后的图片。
    *   下方文本框将显示提取出的特征向量信息。

## 展望 (Future Work)

- [ ] 支持批量处理文件夹中的所有图片。
- [ ] 增加更多的特征提取算法 (如 HOG, SIFT)。
- [ ] 集成更多的分割或目标检测模型 (如 Mask R-CNN, YOLO)。
- [ ] 提供特征向量的降维可视化 (如 t-SNE)。
- [ ] 增加结果导出功能（保存特征向量、标注图片等）。
