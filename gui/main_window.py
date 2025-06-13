import sys
import cv2  # <--- 1. 导入OpenCV
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFileDialog, QTextEdit, QFrame
)
from PyQt6.QtGui import QPixmap, QAction, QFont, QImage # <--- 2. 导入QImage
from PyQt6.QtCore import Qt

import config
from core.preprocessor import preprocess_image # <--- 3. 导入我们的预处理函数

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        # 用于保存处理后的pixmap，以便在窗口缩放时重绘
        self.preprocessed_pixmap = None 
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
        # 将中间的面板命名为 preprocessed_image_label
        middle_panel = self.create_image_panel("预处理图像 (512x512)", "preprocessed_image_label")
        right_panel = self.create_image_panel("主体与部件分割", "segmented_image_label")
        top_layout.addLayout(left_panel, 1)
        top_layout.addLayout(middle_panel, 1)
        top_layout.addLayout(right_panel, 1)
        bottom_layout = QVBoxLayout()
        feature_title = QLabel("特征向量信息")
        feature_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.feature_text = QTextEdit()
        self.feature_text.setReadOnly(True)
        self.feature_text.setText("此处将显示计算出的特征向量...")
        bottom_layout.addWidget(feature_title)
        bottom_layout.addWidget(self.feature_text)
        main_layout.addLayout(top_layout, 4)
        main_layout.addLayout(bottom_layout, 1)

    def create_image_panel(self, title, label_object_name):
        panel_layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label = QLabel(f"{title}将显示在此处")
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setFrameShape(QFrame.Shape.Box)
        image_label.setMinimumSize(300, 300)
        setattr(self, label_object_name, image_label)
        panel_layout.addWidget(title_label)
        panel_layout.addWidget(image_label, 1)
        return panel_layout
    
    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&文件 (File)")
        open_action = QAction("&打开图片 (Open Image)...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.process_new_image)
        file_menu.addAction(open_action)
        exit_action = QAction("&退出 (Exit)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
    def convert_cv_to_pixmap(self, cv_img):
        """ <--- 4. 这是新的核心辅助函数：将OpenCV图像转换为QPixmap """
        # OpenCV图像是BGR格式，而Qt是RGB格式，需要转换
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        
        # 获取图像尺寸和通道信息
        height, width, channel = rgb_image.shape
        bytes_per_line = channel * width
        
        # 创建QImage
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        
        # 从QImage创建QPixmap
        return QPixmap.fromImage(q_image)

    def process_new_image(self):
        """ <--- 5. 这是主要逻辑更新的地方 """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择一张图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff)")
        
        if not file_path:
            return

        self.current_image_path = file_path
        
        # --- 清理旧状态 ---
        self.preprocessed_pixmap = None # 重置
        self.segmented_image_label.setText("待处理...")
        self.feature_text.setText(f"已加载图片: {self.current_image_path}\n正在处理中...")

        # --- 步骤 1: 显示原始图像 ---
        original_pixmap = QPixmap(self.current_image_path)
        self.display_image(self.original_image_label, original_pixmap)

        # --- 步骤 2: 调用核心模块进行预处理 ---
        preprocessed_cv_image = preprocess_image(self.current_image_path)

        # --- 步骤 3: 显示预处理后的图像 ---
        if preprocessed_cv_image is not None:
            self.preprocessed_pixmap = self.convert_cv_to_pixmap(preprocessed_cv_image)
            self.display_image(self.preprocessed_image_label, self.preprocessed_pixmap)
            self.feature_text.append("图像预处理完成。")
        else:
            self.preprocessed_image_label.setText("预处理失败！")
            self.feature_text.append("错误：图像预处理失败。")


    def display_image(self, label, pixmap):
        scaled_pixmap = pixmap.scaled(
            label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        """ <--- 6. 更新resize事件以支持新图像 """
        super().resizeEvent(event) # 先调用父类方法
        if self.current_image_path:
            # 重新加载和显示原始图
            original_pixmap = QPixmap(self.current_image_path)
            self.display_image(self.original_image_label, original_pixmap)
            
        # 如果预处理后的pixmap存在，也对它进行缩放
        if self.preprocessed_pixmap:
            self.display_image(self.preprocessed_image_label, self.preprocessed_pixmap)

        # (未来) 如果有分割图，也在这里重新缩放
        # if hasattr(self, 'segmented_pixmap'):
        #     self.display_image(self.segmented_image_label, self.segmented_pixmap)