# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gaiatest import GaiaTestCase
from gaiatest.apps.phone.app import Phone
from gaiatest.apps.phone.regions.call_screen import CallScreen

from marionette import SkipTest
from marionette.wait import Wait


class TestDeleteCallLog(GaiaTestCase):

    def setUp(self):

        try:
            self.testvars['plivo']
        except KeyError:
            raise SkipTest('Plivo account details not present in test variables')

        GaiaTestCase.setUp(self)

        self.phone = Phone(self.marionette)
        self.phone.launch()

        PLIVO_TIMEOUT = 30

        test_phone_number = self.testvars['remote_phone_number']

        # Make a outgoing call so it will appear in the call log
        self.phone.make_call_and_hang_up(test_phone_number)

        # Wait for fall back to phone app
        self.wait_for_condition(lambda m: self.apps.displayed_app.name == self.phone.name)
        self.apps.switch_to_displayed_app()

        from gaiatest.utils.plivo.plivo_util import PlivoUtil
        self.plivo = PlivoUtil(
            self.testvars['plivo']['auth_id'],
            self.testvars['plivo']['auth_token'],
            self.testvars['plivo']['phone_number']
        )
        # Make a incoming call so it will appear in the call log
        self.call_uuid = self.plivo.make_call(
            to_number=self.testvars['local_phone_numbers'][0].replace('+', ''),
            timeout=30)

        call_screen = CallScreen(self.marionette)
        call_screen.wait_for_incoming_call()
        self.plivo.hangup_call(self.call_uuid)

        Wait(self.plivo, timeout=PLIVO_TIMEOUT).until(
            lambda p: p.is_call_completed(self.call_uuid),
            message="Plivo didn't report the call as completed")
        self.call_uuid = None

        self.apps.switch_to_displayed_app()

    def test_delete_call_log(self):
        """
        https://moztrap.mozilla.org/manage/case/2267/
        """

        call_log = self.phone.tap_call_log_toolbar_button()
        call_log.tap_edit_button()

        # Check that we are in edit mode
        self.assertEqual('Edit', call_log.header_text)

        call_log.tap_select_all_button()
        call_list = call_log.call_list

        # Check that the header contains the number of selected elements
        # and that the checkboxes are selected
        self.assertIn(str(len(call_list)), call_log.header_text)
        for call in call_list:
            self.assertTrue(call.is_checked)

        call_log.tap_delete_button()
        call_log.tap_delete_confirmation_button()

        # Check that the call list is empty
        call_list = call_log.call_list
        self.assertEqual(0, len(call_list))

    def tearDown(self):
        # In case the assertion fails this will still kill the call
        # An open call creates problems for future tests
        self.data_layer.kill_active_call()

        # Also ask Plivo to kill the call if needed
        if self.call_uuid:
            self.plivo.hangup_call(self.call_uuid)

        GaiaTestCase.tearDown(self)
