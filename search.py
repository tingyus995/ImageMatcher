from typing import *
import os
import cv2
import numpy as np

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class IndexedItem:

    def __init__(
            self,
            file_path: str,
            coarse_features: List[int]) -> None:

        self.file_path = file_path
        self.coarse_features = coarse_features


class Engine(QAbstractListModel):

    index_progress_updated = pyqtSignal(float)

    def __init__(self, root_dir: str) -> None:
        super().__init__()
        self.discovered_files: List[str] = []
        self.indexed_items: List[IndexedItem] = []

        for root, dirs, files in os.walk(root_dir):
            for file in files:
                self.discovered_files.append(os.path.join(root, file))

    def _imread(self, path: str):
        try:
            return cv2.imdecode(np.fromfile(file=path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        except:
            return None

    def _extract_coarse_features(self, img: np.ndarray):
        # (h x w x c)
        h, w, c = img.shape
        cx, cy = w // 2, h // 2

        return np.array([
            np.mean(img[0:cy, :cx]).item(),  # top left
            np.mean(img[0:cy, cx:]).item(),  # top right
            np.mean(img[cy:, cx:]).item(),  # bottom right
            np.mean(img[cy:, :cx]).item(),  # bottom left
        ])
    
    def _match(self, img1: np.ndarray, img2: np.ndarray, thresh = 0.25):
        thumb = img1
        full = img2

        if img2.nbytes < img1.nbytes:
            thumb, full = full, thumb

        h, w, c = thumb.shape

        scaled_full = cv2.resize(full, (w, h))

        print(np.abs(np.mean((thumb - scaled_full))))

        return np.abs(np.mean((thumb - scaled_full))) < h * w * thresh

    def start_index(self):

        files_processed = 0

        for file_path in self.discovered_files:

            files_processed += 1

            img = self._imread(file_path)

            if img is not None:
                self.beginInsertRows(QModelIndex(), len(self.indexed_items), len(self.indexed_items))
                self.index_progress_updated.emit(files_processed / len(self.discovered_files))
                print(len(self.indexed_items) / len(self.discovered_files))
                self.indexed_items.append(
                    IndexedItem(
                        file_path=file_path,
                        coarse_features=self._extract_coarse_features(img)
                    )
                )
                self.endInsertRows()
            

    def match(self, img_path):
        target_img = self._imread(img_path)
        
        if target_img is None:
            return

        target_features = self._extract_coarse_features(target_img)

        matched = []

        for item in self.indexed_items:
            if np.abs(np.mean((item.coarse_features - target_features))) <= 3:
                img = self._imread(item.file_path)
                if self._match(target_img, img):
                    matched.append(item.file_path)

        return matched

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.indexed_items)
    

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == Qt.DisplayRole:
            item = self.indexed_items[index.row()]
            return item.file_path