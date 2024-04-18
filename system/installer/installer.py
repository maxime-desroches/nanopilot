import os

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QApplication, QProgressBar

from openpilot.selfdrive.ui.qt.python_helpers import set_main_window
from openpilot.system.updated.updated import get_remote_channel_data, download_update


API_HOST = os.getenv('API_HOST', 'https://api.commadotai.com')
CHANNELS_API_ROOT = "v1/openpilot/channels"


class DownloadWorker(QThread):
  progress = pyqtSignal(int)
  status = pyqtSignal(str)

  def __init__(self, channel):
    super().__init__()
    self.channel = channel

  def download_callback(self, entry, current_index, total):
    self.status.emit("Downloading...")
    self.progress.emit(int((current_index) / total * 100))

  def run(self):
    self.status.emit(f"Fetching channel details {self.channel}")
    build_metadata, manifest = get_remote_channel_data(self.channel)

    if manifest is not None:
      download_update(manifest, self.download_callback)
    else:
      self.status.emit(f"Failed to fetch channel details {self.channel}")

    self.progress.emit(100)
    self.status.emit("Done!")


class Installer(QWidget):
  def __init__(self, parent=None):
    super().__init__(parent)
    layout = QVBoxLayout(self)
    layout.setContentsMargins(150, 290, 150, 150)
    layout.setSpacing(0)

    self.title = QLabel("Installing...")
    self.title.setStyleSheet("font-size: 90px; font-weight: 600;")
    layout.addWidget(self.title, 0, Qt.AlignTop)

    layout.addSpacing(170)

    self.bar = QProgressBar()
    self.bar.setRange(0, 100)
    self.bar.setTextVisible(False)
    self.bar.setFixedHeight(72)
    layout.addWidget(self.bar, 0, Qt.AlignTop)

    layout.addSpacing(30)

    self.val = QLabel("0%")
    self.val.setStyleSheet("font-size: 70px; font-weight: 300;")
    layout.addWidget(self.val, 0, Qt.AlignTop)

    layout.addStretch()

    self.setStyleSheet("""
        * {
          font-family: Inter;
          color: white;
          background-color: black;
        }
        QProgressBar {
          border: none;
          background-color: #292929;
        }
        QProgressBar::chunk {
          background-color: #364DEF;
        }
    """)

  def update_status(self, status):
    self.title.setText(status)

  def update_progress(self, value):
    self.bar.setValue(value)
    self.val.setText(f"{value}%")

  def attach_worker(self, worker: DownloadWorker):
    worker.progress.connect(self.update_progress)
    worker.status.connect(self.update_status)


def main(channel):
  app = QApplication([])

  installer = Installer()
  set_main_window(installer)

  worker = DownloadWorker(channel)
  installer.attach_worker(worker)
  worker.start()

  app.exec_()


if __name__ == "__main__":
  main("nightly")
