import os
import requests

from openpilot.system.hardware import HARDWARE
from openpilot.system.updated.casync.casync import extract, RemoteChunkReader
from openpilot.system.version import BuildMetadata, get_build_metadata, build_metadata_from_dict
from openpilot.system.updated.updated import get_remote_channel_data, download_update


API_HOST = os.getenv('API_HOST', 'https://api.commadotai.com')
CHANNELS_API_ROOT = "v1/openpilot/channels"


def main(channel):
  build_metadata, manifest = get_remote_channel_data(channel)

  if manifest is not None:
    print("downloading manifest: ", manifest)
    download_update(manifest)



if __name__ == "__main__":
  main("nightly")
