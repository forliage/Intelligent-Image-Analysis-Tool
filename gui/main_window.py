import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTextEdit, QFrame  # <--- 1. 在这里添加了 QFrame
)
from PyQt6.QtGui import QPixmap, QAction, QFont
from PyQt6.QtCore import Qt

# 导入配置文件
import config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_path = None  # 用于保存当前打开的图片路径
        self.initUI()

    def initUI(self):
        """初始化主窗口UI"""
        # --- 窗口基本设置 ---
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        # --- 创建菜单栏 ---
        self.create_menu()

        # --- 主布局 ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget) # 整体垂直布局

        # --- 顶部图像显示区 (水平布局) ---
        top_layout = QHBoxLayout()

        # 左侧区域: 原始图 + 预处理图
        left_panel = self.create_image_panel("原始图像", "original_image_label")
        right_panel = self.create_image_panel("预处理图像 (512x512)", "preprocessed_image_label")
        
        # 中间区域: 分割图
        middle_panel = self.create_image_panel("主体与部件分割", "segmented_image_label")

        top_layout.addLayout(left_panel, 1) # 参数1代表拉伸因子
        top_layout.addLayout(right_panel, 1)
        top_layout.addLayout(middle_panel, 1)

        # --- 底部特征向量显示区 ---
        bottom_layout = QVBoxLayout()
        feature_title = QLabel("特征向量信息")
        feature_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.feature_text = QTextEdit()
        self.feature_text.setReadOnly(True)
        self.feature_text.setText("此处将显示计算出的特征向量...")
        
        bottom_layout.addWidget(feature_title)
        bottom_layout.addWidget(self.feature_text)

        # --- 组合布局 ---
        main_layout.addLayout(top_layout, 4) # 顶部占4/5空间
        main_layout.addLayout(bottom_layout, 1) # 底部占1/5空间


    def create_image_panel(self, title, label_object_name):
        """创建一个用于显示图片的面板 (标题 + 图片标签)"""
        panel_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建一个QLabel用于显示图片
        image_label = QLabel(f"{title}将显示在此处")
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # --- 2. 这里是修改的地方 ---
        image_label.setFrameShape(QFrame.Shape.Box) # 设置边框，方便观察
        image_label.setMinimumSize(300, 300) # 设置最小尺寸

        # 将创建的QLabel对象保存为类的属性，方便后续访问
        # setattr(self, 'xxx', yyy) 等同于 self.xxx = yyy
        setattr(self, label_object_name, image_label)

        panel_layout.addWidget(title_label)
        panel_layout.addWidget(image_label, 1) # 最后的1表示该控件在布局中可拉伸
        
        return panel_layout

    def create_menu(self):
        """创建顶部菜单栏"""
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&文件 (File)")

        # 创建“打开图片”动作
        open_action = QAction("&打开图片 (Open Image)...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image_dialog)
        file_menu.addAction(open_action)
        
        # 创建“退出”动作
        exit_action = QAction("&退出 (Exit)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)


    def open_image_dialog(self):
        """打开文件对话框以选择图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择一张图片",
            "", # 默认路径
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_path:
            self.current_image_path = file_path
            # 使用QPixmap加载图片
            pixmap = QPixmap(self.current_image_path)
            # 在“原始图像”标签中显示图片，并保持其宽高比
            self.display_image(self.original_image_label, pixmap)

            # 清空其他区域的提示信息
            self.preprocessed_image_label.setText("待处理...")
            self.segmented_image_label.setText("待处理...")
            self.feature_text.setText(f"已加载图片: {self.current_image_path}")
            
    def display_image(self, label, pixmap):
        """在一个QLabel中显示一个QPixmap，并自适应大小"""
        scaled_pixmap = pixmap.scaled(
            label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)


    def resizeEvent(self, event):
        """重写窗口大小改变事件，确保图片能响应式缩放"""
        if self.current_image_path:
            # 重新加载和显示原始图
            original_pixmap = QPixmap(self.current_image_path)
            self.display_image(self.original_image_label, original_pixmap)
            
            # (未来) 如果有其他图片，也在这里重新缩放
            # if hasattr(self, 'preprocessed_pixmap'):
            #     self.display_image(self.preprocessed_image_label, self.preprocessed_pixmap)
            # if hasattr(self, 'segmented_pixmap'):
            #     self.display_image(self.segmented_image_label, self.segmented_pixmap)

        # 调用父类的resizeEvent以确保其他组件正常缩放
        super().resizeEvent(event)