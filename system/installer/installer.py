import os
import requests

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QStackedLayout, QApplication, QProgressBar, QThread

from openpilot.selfdrive.ui.qt.python_helpers import set_main_window

from openpilot.system.updated.casync.casync import extract, RemoteChunkReader
from openpilot.system.updated.updated import get_remote_channel_data, download_update
from openpilot.system.version import BuildMetadata, get_build_metadata, build_metadata_from_dict


API_HOST = os.getenv('API_HOST', 'https://api.commadotai.com')
CHANNELS_API_ROOT = "v1/openpilot/channels"


class DownloadWorker(QThread):



class Installer(QWidget):
  def __init__(self, parent=None):
    super().__init__(parent)
    layout = QVBoxLayout(self)
    layout.setContentsMargins(150, 290, 150, 150)
    layout.setSpacing(0)

    title = QLabel("Installing...")
    title.setStyleSheet("font-size: 90px; font-weight: 600;")
    layout.addWidget(title, 0, Qt.AlignTop)

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


def main(channel):
  app = QApplication([])

  installer = Installer()
  set_main_window(installer)

  app.exec_()

  build_metadata, manifest = get_remote_channel_data(channel)

  if manifest is not None:
    download_update(manifest)


if __name__ == "__main__":
  main("nightly")
