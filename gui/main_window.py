import sys
import cv2
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFileDialog, QTextEdit, QFrame
)
from PyQt6.QtGui import QPixmap, QAction, QFont, QImage
from PyQt6.QtCore import Qt

import config
from core.preprocessor import preprocess_image
from core.feature_extractor import extract_color_histogram, extract_deep_features
# <--- 1. 导入新的分割函数 ---
from core.segmenter import segment_image_deep, draw_segmentation_mask

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.preprocessed_pixmap = None 
        self.segmented_pixmap = None  # <--- 2. 添加分割图的缓存
        self.initUI()

    def initUI(self):
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.create_menu()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        top_layout = QHBoxLayout()
        left_panel = self.create_image_panel("原始图像", "original_image_label")
        middle_panel = self.create_image_panel("预处理图像", "preprocessed_image_label")
        right_panel = self.create_image_panel("主体与部件分割", "segmented_image_label")
        top_layout.addLayout(left_panel, 1); top_layout.addLayout(middle_panel, 1); top_layout.addLayout(right_panel, 1)
        bottom_layout = QVBoxLayout()
        feature_title = QLabel("特征向量与分析结果"); feature_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.feature_text = QTextEdit(); self.feature_text.setReadOnly(True); self.feature_text.setText("请通过“文件”菜单打开一张图片开始分析...")
        bottom_layout.addWidget(feature_title); bottom_layout.addWidget(self.feature_text)
        main_layout.addLayout(top_layout, 4); main_layout.addLayout(bottom_layout, 1)
        
    def create_image_panel(self, title, label_object_name):
        panel_layout = QVBoxLayout()
        title_label = QLabel(title); title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold)); title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label = QLabel(f"{title}将显示在此处"); image_label.setAlignment(Qt.AlignmentFlag.AlignCenter); image_label.setFrameShape(QFrame.Shape.Box); image_label.setMinimumSize(300, 300)
        setattr(self, label_object_name, image_label)
        panel_layout.addWidget(title_label); panel_layout.addWidget(image_label, 1)
        return panel_layout
    def create_menu(self):
        menu_bar = self.menuBar(); file_menu = menu_bar.addMenu("&文件 (File)")
        open_action = QAction("&打开图片 (Open Image)...", self); open_action.setShortcut("Ctrl+O"); open_action.triggered.connect(self.process_new_image)
        file_menu.addAction(open_action)
        exit_action = QAction("&退出 (Exit)", self); exit_action.setShortcut("Ctrl+Q"); exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    def convert_cv_to_pixmap(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB); height, width, channel = rgb_image.shape; bytes_per_line = channel * width
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888); return QPixmap.fromImage(q_image)

    def process_new_image(self):
        """ <--- 3. 更新处理流程以包含最终的分割步骤 --- """
        file_path, _ = QFileDialog.getOpenFileName(self, "选择一张图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff)")
        if not file_path: return

        self.current_image_path = file_path
        self.preprocessed_pixmap = None
        self.segmented_pixmap = None # 重置
        
        self.feature_text.setText(f"已加载图片: {self.current_image_path}\n")
        QApplication.processEvents()

        # 步骤1: 显示原始图
        original_pixmap = QPixmap(self.current_image_path)
        self.display_image(self.original_image_label, original_pixmap)

        # 步骤2: 预处理
        self.feature_text.append("正在进行图像预处理..."); QApplication.processEvents()
        preprocessed_cv_image = preprocess_image(self.current_image_path)
        if preprocessed_cv_image is None: self.feature_text.append("错误：预处理失败。"); return
        self.preprocessed_pixmap = self.convert_cv_to_pixmap(preprocessed_cv_image)
        self.display_image(self.preprocessed_image_label, self.preprocessed_pixmap)
        self.feature_text.append("图像预处理完成。\n"); QApplication.processEvents()
        
        # 步骤3: 特征提取
        self.feature_text.append("正在提取特征向量..."); QApplication.processEvents()
        _, hist_desc = extract_color_histogram(preprocessed_cv_image)
        self.feature_text.append(hist_desc)
        QApplication.processEvents()
        _, deep_desc = extract_deep_features(preprocessed_cv_image)
        self.feature_text.append(deep_desc)
        self.feature_text.append("\n特征提取完成。\n"); QApplication.processEvents()
        
        # 步骤4: 图像分割 (最终步骤)
        self.feature_text.append("正在进行图像分割 (此步骤可能较慢)..."); QApplication.processEvents()
        segmentation_mask = segment_image_deep(preprocessed_cv_image)
        
        # 将分割结果绘制到预处理后的图像上
        segmented_image = draw_segmentation_mask(preprocessed_cv_image, segmentation_mask)
        self.segmented_pixmap = self.convert_cv_to_pixmap(segmented_image)
        self.display_image(self.segmented_image_label, self.segmented_pixmap)
        self.feature_text.append("图像分割完成。"); QApplication.processEvents()

        self.feature_text.append("\n所有任务处理完成！")

    def display_image(self, label, pixmap):
        scaled_pixmap = pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        """ <--- 4. 更新resize事件以支持分割图 --- """
        super().resizeEvent(event)
        if self.current_image_path:
            self.display_image(self.original_image_label, QPixmap(self.current_image_path))
        if self.preprocessed_pixmap:
            self.display_image(self.preprocessed_image_label, self.preprocessed_pixmap)
        if self.segmented_pixmap: # 新增
            self.display_image(self.segmented_image_label, self.segmented_pixmap)