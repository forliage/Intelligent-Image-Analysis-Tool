import sys
import os
import torch.hub
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def setup_torch_hub_dir():
    """
    设置PyTorch Hub的缓存目录到项目根目录下的 'models' 文件夹。
    这可以确保所有下载的模型都保存在项目内部。
    """
    # 获取当前脚本所在的目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    # 定义模型要存放的目录
    models_dir = os.path.join(project_root, "models")
    
    # 如果目录不存在，则创建它
    os.makedirs(models_dir, exist_ok=True)
    
    # 设置PyTorch Hub的目录
    torch.hub.set_dir(models_dir)
    
    print(f"PyTorch Hub directory set to: {models_dir}")


if __name__ == '__main__':
    # 在启动任何PyTorch相关操作之前，首先设置好下载目录
    setup_torch_hub_dir()

    # 创建PyQt应用实例
    app = QApplication(sys.argv)

    # 创建主窗口实例
    main_win = MainWindow()

    # 显示窗口
    main_win.show()

    # 进入程序的主循环，并通过sys.exit()确保程序能完整退出
    sys.exit(app.exec())