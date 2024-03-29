#!/usr/bin/env python3

import unittest

from openpilot.selfdrive.car.values import PLATFORMS


class TestPlatformConfigs(unittest.TestCase):
  def test_configs(self):

    for name, platform in PLATFORMS.items():
      with self.subTest(platform=str(platform)):
        # TODO: fix
        # self.assertTrue(platform.value._frozen)

        if platform != "MOCK":
          self.assertIn("pt", platform.value.dbc_dict)

        self.assertIsNotNone(platform.value.specs)


if __name__ == "__main__":
  unittest.main()
