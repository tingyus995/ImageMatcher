from ast import arg
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from search import Engine

from utils import DirChooser, FileChooser
from threading import Thread


class Window(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        self.main_layout = QHBoxLayout()

        self.left_panel_layout = QVBoxLayout()

        self.left_panel_layout.addWidget(QLabel("Search Directory:"))
        self.root_dir_chooser = DirChooser()
        self.left_panel_layout.addWidget(self.root_dir_chooser)

        self.left_panel_layout.addWidget(QLabel("Target Image"))
        self.target_file_chooser = FileChooser(title = 'Choose target image', filter = "Image Files (*.jpg *.jpeg *.png)")
        self.left_panel_layout.addWidget(self.target_file_chooser)

        self.index_btn = QPushButton("index")
        self.index_btn.clicked.connect(self._init_engine)
        self.left_panel_layout.addWidget(self.index_btn)

        self.match_btn = QPushButton("match")
        self.match_btn.clicked.connect(self._handle_match_btn)
        self.left_panel_layout.addWidget(self.match_btn)

        self.log_tb = QTextEdit()
        self.left_panel_layout.addWidget(self.log_tb)

        self.left_panel_layout.addStretch()
        self.main_layout.addLayout(self.left_panel_layout)

        self.picture_view_lb = QLabel()
        self.main_layout.addWidget(self.picture_view_lb)

        self.right_panel_layout = QVBoxLayout()
        self.index_pb = QProgressBar()
        self.index_pb.setMaximum(100)
        self.index_pb.setMinimum(0)
        self.index_pb.setValue(0)
        self.right_panel_layout.addWidget(self.index_pb)

        self.indexed_files_lv = QListView()
        self.right_panel_layout.addWidget(self.indexed_files_lv)

        self.main_layout.addLayout(self.right_panel_layout)


        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)
    
    def _handle_match_btn(self):
        matched = self.engine.match(self.target_file_chooser.get_path())
        self.log_tb.append('\n'.join(matched))
    
    def _handle_selection_changed(self):
        path = self.engine.data(self.indexed_files_lv.selectionModel().selectedIndexes()[0], Qt.DisplayRole)
        pixmap = QPixmap(path)
        self.picture_view_lb.setPixmap(pixmap.scaledToWidth(300))
    def _init_engine(self):

        self.engine = Engine(self.root_dir_chooser.get_path())
        self.engine.index_progress_updated.connect(lambda p: self.index_pb.setValue(int(p * 100)))
        Thread(target=lambda: self.engine.start_index()).start()

        self.indexed_files_lv.setModel(self.engine)
        self.indexed_files_lv.selectionModel().selectionChanged.connect(self._handle_selection_changed)



app = QApplication([])
win = Window()
win.show()
app.exec()