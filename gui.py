import pathlib
import time
import sys
import enum
import gui_data
from hashlib import sha256
from PySide6.QtCore import (QThread, Signal, QObject, QDir, Qt)
from PySide6.QtWidgets import (
    QGridLayout, QBoxLayout, QMainWindow, QApplication, QPushButton, QGroupBox, QLabel, QWidget, QFileDialog, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QSizePolicy, QHBoxLayout, QToolButton, QMenu)


class FS_FLAGS(enum.Enum):
    FS_FOLDER = 0
    FS_FILE = 1


class EventEmitter(QObject):
    sig = Signal(str)
    add_id_signal = Signal(int)
    add_file_signal = Signal(str)
    add_hash_signal = Signal(str)


class HashFile(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.signal = EventEmitter()

    def add_file(self, filename):
        self.filename = filename

    def run(self):
        with open(self.filename, "rb") as f:
            bytes = f.read()
            shahash = sha256(bytes).hexdigest()
        self.exiting = True
        self.signal.add_hash_signal.emit(str(shahash))


class PatchPicker(QGridLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.signal = EventEmitter()
        self._instances = {}
        self.game_engine_label = QLabel("Choose game engine")
        self.patch_label = QLabel("Choose patch")
        self.engine_combo = QComboBox()
        self.patch_combo = QComboBox()
        self.patch_button = QPushButton("&Patch")
        self.patch_combo.setEditable(False)
        self.engine_combo.setEditable(False)
        self.patch_combo.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.engine_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.patches = gui_data.GamePatcher()
        self.game_engines = gui_data.GameEngineText()
        self.engine_combo.addItems(self.game_engines.get_titles())
        self.engine_combo.currentTextChanged.connect(self.change_patch_type)
        self.patch_button.clicked.connect(self.patch_it)
        self.patches.set_engine(self.game_engines.title_to_key(
            self.engine_combo.currentText()))

        self.addWidget(self.game_engine_label, 0, 0)
        self.addWidget(self.patch_label, 1, 0)
        self.addWidget(self.engine_combo, 0, 1)
        self.addWidget(self.patch_combo, 1, 1)
        self.addWidget(self.patch_button, 2, 1)

    def change_patch_type(self, game_engine):
        self.patch_combo.clear()
        self.patches.set_engine(self.game_engines.title_to_key(
            self.engine_combo.currentText()))
        self.patch_combo.addItems(self.patches.get_titles())

    def add_instance(self, instance_name, instance):
        self._instances[instance_name] = instance

    def patch_it(self):
        func = self.patches.get_patch('Freeze fix')
        files = []
        for row in range(self._instances["file_table"].table.rowCount()):
            if self._instances["file_table"].table.item(row, 0).checkState() is Qt.CheckState.Checked:
                files.append(
                    self._instances["file_table"].table.item(row, 0).text())

        for file in files:
            func(file)
    pass


class PathPicker(QGridLayout):
    def __init__(self):
        super().__init__()
        self.signal = EventEmitter()

        self.file_label = QLabel("Location")
        self.path_input = QLineEdit()
        #self.browse_button = QPushButton("&Browse")
        self.browse_button = QToolButton()
        self.add_button = QPushButton("&Add")
        self.add_button.clicked.connect(self.add_data_filetable)

        self.browse_button.setText("&Browse")
        self.browse_button.setCursor(Qt.ArrowCursor)
        self.browse_button.clicked.connect(self.file_browser)

        self.browse_button.setPopupMode(QToolButton.MenuButtonPopup)
        self.fs_menu = QMenu()
        self.fs_menu.addAction("Folder", self.set_folder_mode)
        self.fs_menu.addAction("File", self.set_file_mode)
        self.browse_button.setMenu(self.fs_menu)
        self.addWidget(self.file_label, 0, 0)
        self.addWidget(self.path_input, 0, 1)
        self.addWidget(self.browse_button, 0, 2)
        self.addWidget(self.add_button, 0, 3,)

        self._fs_mode = None

    def set_folder_mode(self):
        self._fs_mode = FS_FLAGS.FS_FOLDER
        self.add_button.setText("&Add folder")

    def set_file_mode(self):
        self._fs_mode = FS_FLAGS.FS_FILE
        self.add_button.setText("&Add file")

    def add_data_filetable(self):
        if pathlib.Path(self.path_input.text()).exists():
            self.signal.add_file_signal.emit(self.path_input.text())
        pass

    def file_browser(self):
        if self._fs_mode == FS_FLAGS.FS_FILE:
            fs_object = QFileDialog.getOpenFileName(
                caption="Game file to patch", dir=QDir.currentPath())
            fs_object = fs_object[0]
        elif self._fs_mode == FS_FLAGS.FS_FOLDER:
            fs_object = QFileDialog.getExistingDirectory(
                caption="Game folder to patch", dir=QDir.currentPath())
            pass
        else:
            fs_object = QFileDialog.getOpenFileName(
                caption="Game file to patch", dir=QDir.currentPath())
            fs_object = fs_object[0]

        self.path_input.setText(fs_object)

    pass


class FileTable(QGridLayout):
    def __init__(self, headers):
        super().__init__()
        self.signal = EventEmitter()
        self.path_input = PathPicker()
        self.table = QTableWidget(0, 3)
        self.thread = HashFile()
        self.file_dict = {
            "id": 0,
            "path_item": None,
        }
        self.signal.add_id_signal.connect(self.add_id)
        self.path_input.signal.add_file_signal.connect(self.add_file)
        self.thread.signal.add_hash_signal.connect(self.add_hash)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch)
        self.addLayout(self.path_input, 0, 0)
        self.addWidget(self.table, 1, 0)

    def add_id(self, id):
        self.file_dict["id"] = id
        pass

    def add_hash(self, hashsum):
        if not self.thread.isRunning():
            self.thread.start()
        if len(self.table.findItems(hashsum, Qt.MatchExactly)) > 0:
            return
        hash_item = QTableWidgetItem(hashsum)
        row = self.file_dict["id"]
        print(row)
        self.table.editItem(self.file_dict["path_item"])
        self.table.setItem(row, 1, hash_item)
        pass

    def add_file(self, data):
        if len(self.table.findItems(data, Qt.MatchExactly)) > 0 or len(data) <= 0:
            return
        path_item = QTableWidgetItem(data)
        path_item.setFlags(path_item.flags() |
                           Qt.ItemIsEditable | Qt.ItemIsUserCheckable)

        row = self.table.rowCount()
        self.signal.add_id_signal.emit(row)
        self.thread.add_file(data)
        self.thread.start()

        path_item.setCheckState(Qt.Checked)
        self.table.insertRow(row)
        self.table.setItem(row, 0, path_item)
        self.file_dict["path_item"] = path_item


# class FileGroup(QGroupBox):
#    def __init__(self):
#        super.__init__()
#    pass


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.centralWidget = QWidget(self)
        self.mainLayout = QGridLayout()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.mainLayout)

        self.setWindowTitle("Game Patcher")
        self.resize(500, 300)

    def appendWidget(self, widget, row, column, rowSpan=None, columnSpan=None):
        if rowSpan is None or columnSpan is None:
            self.mainLayout.addWidget(widget, row, column)
        else:
            self.mainLayout.addWidget(widget, row, column, rowSpan, columnSpan)

    def appendLayout(self, layout, row, column, rowSpan=None, columnSpan=None, alignment=None) -> None:
        if rowSpan is None or columnSpan is None:
            self.mainLayout.addLayout(layout, row, column)
        else:
            self.mainLayout.addLayout(layout, row, column, rowSpan, column)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    filetable_widget = FileTable(("Location", "Hash", "Patched"))
    patch_picker = PatchPicker()
    patch_picker.add_instance("file_table", filetable_widget)
    patch_group = QGroupBox("Patch settings")
    file_group = QGroupBox("Add paths")

    patch_group.setLayout(patch_picker)
    file_group.setLayout(filetable_widget)
    window.appendWidget(patch_group, 0, 0)
    window.appendWidget(file_group, 1, 0)

    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
