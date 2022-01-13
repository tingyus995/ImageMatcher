from turtle import title
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class DirChooser(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.main_layout = QHBoxLayout()
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self._open_dialog)
        self.main_layout.addWidget(self.browse_btn)

        self.path_le = QLineEdit()
        self.main_layout.addWidget(self.path_le)

        self.setLayout(self.main_layout)
    
    def _open_dialog(self):

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.exec()
        self.path_le.setText(dialog.directory().absolutePath())
    
    def get_path(self):
        return self.path_le.text()

class FileChooser(DirChooser):
    def __init__(self, title: str, filter: str) -> None:
        super().__init__()
        self.title = title
        self.filter = filter

    def _open_dialog(self):
        url, _ = QFileDialog.getOpenFileName(self, self.title, filter=self.filter)
        print(url)
        self.path_le.setText(url)
