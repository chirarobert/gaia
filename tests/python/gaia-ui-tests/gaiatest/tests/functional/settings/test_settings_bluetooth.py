# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import time

from gaiatest import GaiaTestCase
from gaiatest.apps.settings.app import Settings


class TestBluetoothSettings(GaiaTestCase):

    def setUp(self):
        GaiaTestCase.setUp(self)

        # Bluetooth host object
        from gaiatest.utils.bluetooth.bluetooth_host import BluetoothHost
        self.bluetooth_host = BluetoothHost(self.marionette)

    def test_toggle_bluetooth_settings(self):
        """Toggle Bluetooth via Settings - Networks & Connectivity

        https://moztrap.mozilla.org/manage/case/6071/
        """

        settings = Settings(self.marionette)
        settings.launch()

        bluetooth_settings = settings.open_bluetooth_settings()
        bluetooth_settings.enable_bluetooth()

        bluetooth_settings.enable_visible_to_all()
        device_name = bluetooth_settings.device_name

        # Now have host machine inquire and shouldn't find our device
        device_found = self.bluetooth_host.is_device_visible(device_name)
        self.assertTrue(device_found, "Host should see our device (device discoverable mode is ON)")
