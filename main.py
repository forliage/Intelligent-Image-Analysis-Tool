import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

if __name__ == '__main__':
    # 创建PyQt应用实例
    app = QApplication(sys.argv)

    # 创建主窗口实例
    main_win = MainWindow()

    # 显示窗口
    main_win.show()

    # 进入程序的主循环，并通过sys.exit()确保程序能完整退出
    sys.exit(app.exec())